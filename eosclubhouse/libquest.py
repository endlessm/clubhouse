# Copyright (C) 2018 Endless Mobile, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Authors:
#       Joaquim Rocha <jrocha@endlessm.com>
#

import asyncio
import functools
import glibcoro
import os
import pkgutil
import sys
import threading
import time

from enum import Enum
from eosclubhouse import config, logger
from eosclubhouse.system import App, Desktop, GameStateService, Sound
from eosclubhouse.utils import get_alternative_quests_dir, Performance, QuestStringCatalog, QS
from gi.repository import GObject, GLib, Gio


# Set up the asyncio loop implementation
glibcoro.install()


class Registry:

    _quest_sets = []

    @staticmethod
    @Performance.timeit
    def load(quest_folder):
        sys.path.append(quest_folder)

        for _unused, modname, _unused in pkgutil.walk_packages([quest_folder]):
            __import__(modname)

        del sys.path[sys.path.index(quest_folder)]

    @classmethod
    @Performance.timeit
    def register_quest_set(class_, quest_set):
        if not issubclass(quest_set, QuestSet):
            raise TypeError('{} is not a of type {}'.format(quest_set, QuestSet))
        class_._quest_sets.append(quest_set())
        logger.info('QuestSet registered: %s', quest_set)

    @classmethod
    def get_quest_sets(class_):
        return class_._quest_sets

    @classmethod
    def get_quest_set_by_name(class_, name):
        for quest_set in class_.get_quest_sets():
            if quest_set.get_id() == name:
                return quest_set

        return None

    @classmethod
    def has_quest_sets_highlighted(class_):
        return any(qs.highlighted for qs in class_._quest_sets)

    @classmethod
    def get_quest_by_name(class_, name):
        quest_set_name = None
        name_split = name.split('.', 1)

        if len(name_split) > 1:
            quest_set_name, quest_name = name_split
        else:
            quest_name = name

        for quest_set in class_.get_quest_sets():
            if quest_set_name is not None and quest_set_name != quest_set.get_id():
                continue

            for quest in quest_set.get_quests():
                if quest.get_id() == quest_name:
                    return quest

        return None

    @classmethod
    def load_current_episode(class_):
        class_.load(get_alternative_quests_dir())
        current_episode = class_.get_current_episode()
        class_.load(os.path.join(os.path.dirname(__file__),
                                 'quests',
                                 current_episode['name']))

    @classmethod
    def get_available_episodes(class_):
        episodes_path = os.path.join(os.path.dirname(__file__), 'quests')
        episodes = os.listdir(episodes_path)
        return (e for e in episodes if os.path.isdir(os.path.join(episodes_path, e)))

    @classmethod
    def get_current_episode(class_):
        current_episode_name = config.DEFAULT_EPISODE_NAME
        current_episode_completed = False
        current_episode_teaser_viewed = False
        current_episode = GameStateService().get('clubhouse.CurrentEpisode')
        if current_episode is not None:
            current_episode_name = current_episode.get('name', config.DEFAULT_EPISODE_NAME)
            current_episode_completed = current_episode.get('completed', False)
            current_episode_teaser_viewed = current_episode.get('teaser-viewed', False)
        return {
            'name': current_episode_name,
            'completed': current_episode_completed,
            'teaser-viewed': current_episode_teaser_viewed,
        }

    @classmethod
    def set_current_episode(class_, episode_name):
        if episode_name not in class_.get_available_episodes():
            raise KeyError
        if episode_name == class_.get_current_episode()['name']:
            return

        logger.info('Setting episode: %s', episode_name)
        episode_info = {'name': episode_name, 'completed': False, 'teaser-viewed': False}
        GameStateService().set('clubhouse.CurrentEpisode', episode_info)

    @classmethod
    def set_current_episode_teaser_viewed(class_, viewed):
        current_episode_info = class_.get_current_episode()
        if not current_episode_info['completed']:
            return

        current_episode_info.update({'teaser-viewed': viewed})
        GameStateService().set('clubhouse.CurrentEpisode', current_episode_info)


class _QuestRunContext:

    def __init__(self, cancellable):
        self._confirm_action = None

        asyncio.set_event_loop(asyncio.new_event_loop())

        self._step_loop = asyncio.new_event_loop()
        self._timeout_handle = None
        self._cancellable = cancellable
        self._debug_actions = set()

    def _cancel_and_close_loop(self, loop):
        if not loop.is_closed():
            for task in asyncio.Task.all_tasks(loop=loop):
                task.cancel()

            loop.stop()
            loop.close()

    def _cancel_all(self):
        self.reset_stop_timeout()

        self._cancel_and_close_loop(self._step_loop)

        # Cancel also any ongoing actions
        self._cancel_and_close_loop(asyncio.get_event_loop())

    def user_confirmed(self):
        if self._confirm_action is not None:
            self._confirm_action.resolve()
            self._confirm_action = None

    def get_confirm_action(self):
        if self._confirm_action is None or self._confirm_action.future.done():
            self._confirm_action = self.new_async_action()

        return self._confirm_action

    def cancel(self):
        self._cancellable.cancel()

    def reset_stop_timeout(self):
        if self._timeout_handle is not None:
            self._timeout_handle.cancel()
            self._timeout_handle = None

    def run_stop_timeout(self, timeout):
        self.reset_stop_timeout()
        self._timeout_handle = self._step_loop.call_later(timeout, self.cancel)

    def set_next_step(self, step_func, *args):
        def _run_step(step_func_data):
            step_func, args_ = step_func_data

            # Execute the step
            result = step_func(*args_)

            if result is None or self._cancellable.is_cancelled():
                return

            # Set the next step according to the result
            next_step_func = result
            next_step_args = ()

            if isinstance(result, tuple):
                if len(result) > 1:
                    next_step_func = result[0]

                next_step_args = result[1:]

            self.set_next_step(next_step_func, *next_step_args)

        if self._cancellable.is_cancelled() or self._step_loop.is_closed():
            return

        self._step_loop.call_soon(functools.partial(_run_step, (step_func, args)))

    def run(self, first_step=None):
        if self._cancellable.is_cancelled():
            return

        self._cancellable.connect(self._cancel_all)

        if first_step is not None:
            self.set_next_step(first_step)

        self._step_loop.run_forever()

    def new_async_action(self, future=None):
        async_action = AsyncAction()

        async_action.run_context = self
        async_action.future = future or self._new_future()

        if self._cancellable.is_cancelled():
            async_action.cancel()
            return async_action

        return async_action

    def _new_future(self):
        # Renew the event loop if needed
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())

        return asyncio.get_event_loop().create_future()

    def _future_get_loop(self, future):
        # @todo: when we have Python 3.7 we can use the loop from the future's get_loop function
        # directly; for now, we have to check what's the best way
        if hasattr(future, 'get_loop'):
            return future.get_loop()

        return future._loop

    def pause(self, secs):
        async_action = self.new_async_action()

        if async_action.is_cancelled():
            return async_action

        loop = self._future_get_loop(async_action.future)
        loop.call_later(secs, functools.partial(async_action.resolve))

        return self.wait_for_action(async_action)

    def wait_for_action(self, async_action, timeout=None):
        return self.wait_for_one([async_action], timeout)[0]

    def wait_for_one(self, action_list, timeout=None):
        futures = []

        if len(action_list) == 0:
            return action_list

        for async_action in action_list:
            async_action.state = AsyncAction.State.PENDING
            futures.append(async_action.future)

        async def wait_or_timeout(futures, timeout=None):
            pending = []

            try:
                _done, pending = await asyncio.wait(futures, timeout=timeout,
                                                    return_when=asyncio.FIRST_COMPLETED)
            except asyncio.TimeoutError:
                logger.debug('Wait for action timed out.')
            except asyncio.CancelledError:
                logger.debug('Wait for action cancelled.')
            else:
                logger.debug('Wait for action finished.')

            for future in pending:
                future.cancel()

        self._debug_actions = set(action_list)

        loop = asyncio.new_event_loop()
        loop.run_until_complete(wait_or_timeout(futures, timeout))
        loop.stop()
        loop.close()

        self._debug_actions.clear()

        # Cancel any pending actions
        for future in filter(lambda future: not future.done(), futures):
            try:
                future.cancel()
            except asyncio.InvalidStateError:
                # It may happen that the loop is already closed at this moment, but we just
                # ignore this issue since the future is still correctly cancelled.
                pass

        # Update the AsyncActions' states accordingly
        for async_action in action_list:
            future = async_action.future
            if future.cancelled():
                async_action.state = AsyncAction.State.CANCELLED
            elif future.done():
                async_action.state = AsyncAction.State.DONE

        return action_list

    def debug_dispatch(self):
        if not self._cancellable.is_cancelled():
            for action in self._debug_actions:
                action.resolve()

        self._debug_actions = set()


class AsyncAction:

    State = Enum('State', ['UNKNOWN', 'DONE', 'CANCELLED', 'PENDING'])

    def __init__(self):
        self._state = self.State.UNKNOWN
        self.run_context = None
        self.future = None

    def is_done(self):
        return self._state == self.State.DONE

    def is_cancelled(self):
        return self._state == self.State.CANCELLED

    def is_pending(self):
        return self._state == self.State.PENDING

    def resolve(self):
        if self.future is not None and not self.future.done():
            self.future.set_result(True)

    def cancel(self):
        if self.future is not None and not self.future.done():
            self.future.cancel()
        self._state = self.State.CANCELLED

    def is_resolved(self):
        if self.future is not None:
            return self.future.done()

        return self._state != self.State.PENDING and self._state != self.State.UNKNOWN

    def wait(self, timeout=None):
        if not self.is_resolved():
            assert self.run_context is not None
            self.run_context.wait_for_action(self, timeout)
        return self

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state


class Quest(GObject.GObject):

    __gsignals__ = {
        'message': (
            GObject.SignalFlags.RUN_FIRST, None, (str, GObject.TYPE_PYOBJECT, str, str, str, str)
        ),
        'item-given': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str)
        ),
        'dismissed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _DEFAULT_TIMEOUT = 2 * 3600  # secs

    skippable = GObject.Property(type=bool, default=False)
    stop_timeout = GObject.Property(type=int, default=_DEFAULT_TIMEOUT)
    continue_message = GObject.Property(type=str, default="You haven't completed my challenge yet!")
    accept_label = GObject.Property(type=str, default="Sure!")
    reject_label = GObject.Property(type=str, default="Not now…")

    def __init__(self, name, main_character_id, initial_msg=None):
        super().__init__()
        self._name = name

        self._qs_base_id = self.get_default_qs_base_id()
        self._initial_msg = initial_msg

        self._last_bg_sound_uuid = None
        self._last_bg_sound_event_id = None

        if self._initial_msg is None:
            self._initial_msg = self._get_initial_msg_from_qs()

            label = self._get_accept_label_from_qs()
            if label:
                self.accept_label = label

            label = self._get_reject_label_from_qs()
            if label:
                self.reject_label = label

        if self._initial_msg is None:
            logger.critical('Initial message is missing for quest %r', self._qs_base_id)

        self._characters = {}

        self._main_character_id = main_character_id
        self._main_mood = 'talk'
        self._main_open_dialog_sound = 'clubhouse/dialog/open'
        self._default_abort_sound = 'quests/quest-aborted'

        self._available = True
        self._cancellable = None

        self.gss = GameStateService()

        self.conf = {}
        self.load_conf()

        self.key_event = False
        self._debug_skip = False

        self._confirmed_step = False

        self._run_context = None

    def get_default_qs_base_id(self):
        return str(self.__class__.__name__).upper()

    def _get_initial_msg_from_qs(self):
        return QS('{}_QUESTION'.format(self._qs_base_id))

    def _get_accept_label_from_qs(self):
        return QS('{}_QUEST_ACCEPT'.format(self._qs_base_id))

    def _get_reject_label_from_qs(self):
        return QS('{}_QUEST_REJECT'.format(self._qs_base_id))

    def run(self, on_quest_finished):
        if hasattr(self, 'step_begin'):
            self.run_in_context(on_quest_finished)
        else:
            self.run_in_thread(on_quest_finished)

    def run_in_thread(self, on_quest_finished):
        def _on_task_finished(quest, result):
            nonlocal on_quest_finished
            on_quest_finished(quest)

        def _run_task_in_thread(task):
            quest = task.get_source_object()
            quest.start()
            task.return_boolean(True)

        quest_task = Gio.Task.new(self, self.get_cancellable(), _on_task_finished)
        threading.Thread(target=_run_task_in_thread, args=(quest_task,),
                         name='quest-thread').start()

    def run_in_context(self, quest_finished_cb):
        Sound.play('quests/quest-given')

        self._run_context = _QuestRunContext(self._cancellable)
        self._run_context.run(self.step_begin)
        self._run_context = None

        quest_finished_cb(self)

    def start(self):
        '''Start the quest's main function

        This method runs the quest as a step-by-step approach, so a method called 'step_first'
        needs to be defined in any Quest subclasses that want to follow this approach.

        As an alternative, subclasses can override this very method in order to follow any
        approach needed.
        '''

        sleep_time = .1  # sec
        time_in_step = 0
        step_func = self.step_first

        times_failed = 0
        last_exception = None

        Sound.play('quests/quest-given')

        while not self.is_cancelled():
            try:
                new_func = step_func(time_in_step)
            except Exception as e:
                if (type(e) is type(last_exception) and
                        e.args == last_exception.args):
                    times_failed += 1
                    if times_failed > 10:
                        logger.critical('Quest step failed 10 times, bailing',
                                        exc_info=sys.exc_info())
                        self.stop()
                        return
                else:
                    last_exception = e
                    times_failed = 1

                logger.warning('Quest step failed, retrying',
                               exc_info=sys.exc_info())

                time.sleep(sleep_time)
                time_in_step += sleep_time

                continue

            times_failed = 0
            last_exception = None

            if new_func is None:
                time.sleep(sleep_time)
                time_in_step += sleep_time
            else:
                step_func = new_func
                time_in_step = 0

            self._check_timed_out(time_in_step)

        self._reset_timeout()

    def set_next_step(self, step_func, delay=0, args=()):
        assert self._run_context is not None
        self._run_context.set_next_step(step_func, delay, args)

    def wait_for_app_launch(self, app, timeout=None, pause_after_launch=0):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()
        if async_action.is_cancelled():
            return async_action

        if app.is_running():
            async_action.state = AsyncAction.State.DONE
            return async_action

        def _on_app_running_changed(app, async_action):
            if app.is_running() and not async_action.is_resolved():
                async_action.resolve()

        handler_id = app.connect_running_change(_on_app_running_changed, app, async_action)

        self._run_context.wait_for_action(async_action, timeout)

        app.disconnect_running_change(handler_id)

        if async_action.is_done() and pause_after_launch > 0:
            self.pause(pause_after_launch)

        return async_action

    def wait_for_app_js_props_changed(self, app, props, timeout=None):
        return self.connect_app_js_props_changes(app, props).wait(timeout)

    def wait_for_app_in_foreground(self, app, timeout=None):
        assert self._run_context is not None
        async_action = self._run_context.new_async_action()

        if Desktop.is_app_in_foreground(app.dbus_name):
            async_action.state = AsyncAction.State.DONE
            return async_action

        def _on_app_running_changed(app, async_action):
            if not app.is_running() and not async_action.is_resolved():
                async_action.resolve()

        def _on_app_in_foreground_changed(app_in_foreground_name, app_name, async_action):
            app_name = Desktop.get_app_desktop_name(app_name)
            if app_in_foreground_name == app_name and not async_action.is_resolved():
                async_action.resolve()

        if async_action.is_cancelled():
            return async_action

        in_foreground_handler_id = Desktop.connect_app_in_foreground_change(
            _on_app_in_foreground_changed, app.dbus_name, async_action)
        running_handler_id = app.connect_running_change(_on_app_running_changed, app, async_action)

        self._run_context.wait_for_action(async_action, timeout)

        Desktop.disconnect_app_in_foreground_change(in_foreground_handler_id)
        app.disconnect_running_change(running_handler_id)

        return async_action

    def connect_app_js_props_changes(self, app, props):
        assert len(props) > 0
        return self._connect_app_changes(app, props)

    def connect_app_quit(self, app):
        return self._connect_app_changes(app, [])

    def _connect_app_changes(self, app, props):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()

        def _on_app_running_changed(app, async_action):
            if not app.is_running() and not async_action.is_resolved():
                async_action.resolve()

        js_props_handler_id = running_handler_id = 0

        def _disconnect_app(_future):
            nonlocal js_props_handler_id
            nonlocal running_handler_id

            if js_props_handler_id > 0:
                app.disconnect_js_props_change(js_props_handler_id)
                js_props_handler_id = 0

            app.disconnect_running_change(running_handler_id)

        if not app.is_running():
            async_action.cancel()

        if async_action.is_cancelled():
            return async_action

        async_action.future.add_done_callback(_disconnect_app)

        if len(props) > 0:
            try:
                js_props_handler_id = app.connect_js_props_change(props,
                                                                  lambda: async_action.resolve())
            except GLib.Error as e:
                # Prevent any D-Bus errors (like ServiceUnknown when the app has been quit)
                logger.debug('Could not connect to app "%s" js property changes: %s',
                             app.dbus_name, e.get_message())

                async_action.cancel()
                return async_action

        running_handler_id = app.connect_running_change(_on_app_running_changed, app, async_action)

        return async_action

    def connect_gss_changes(self):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()

        gss_changes_handler_id = 0

        def _disconnect_gss(_future):
            self.gss.disconnect(gss_changes_handler_id)

        if async_action.is_cancelled():
            return async_action

        async_action.future.add_done_callback(_disconnect_gss)

        gss_changes_handler_id = self.gss.connect('changed', lambda _gss: async_action.resolve())

        return async_action

    def connect_settings_changes(self, settings, keys_list):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()

        if async_action.is_cancelled():
            return async_action

        settings_changes_handler_id = 0

        def _disconnect_settings(_future=None):
            nonlocal settings_changes_handler_id
            nonlocal settings
            if settings_changes_handler_id > 0:
                settings.disconnect(settings_changes_handler_id)
                settings_changes_handler_id = 0

        def _on_settings_changed(_settings, key, keys_list):
            _disconnect_settings()
            if key in keys_list:
                async_action.resolve()

        async_action.future.add_done_callback(_disconnect_settings)

        settings_changes_handler_id = settings.connect('changed', _on_settings_changed, keys_list)

        return async_action

    def pause(self, secs):
        assert self._run_context is not None
        return self._run_context.pause(secs)

    def wait_confirm(self, msg_id=None, timeout=None):
        return self.show_confirm_message(msg_id).wait(timeout)

    def get_confirm_action(self):
        assert self._run_context is not None

        async_action = self._run_context.get_confirm_action()
        return async_action

    def show_confirm_message(self, msg_id, **options):
        assert self._run_context is not None

        async_action = self.get_confirm_action()
        if async_action.is_cancelled():
            return async_action

        self._confirmed_step = False
        options.update({'use_confirm': True})
        self.show_message(msg_id, **options)

        return async_action

    def wait_for_one(self, action_list):
        self._run_context.wait_for_one(action_list)

    def set_to_background(self):
        if self._run_context is not None:
            if self._last_bg_sound_uuid:
                Sound.stop(self._last_bg_sound_uuid)
                self._last_bg_sound_uuid = None
            self._run_context.run_stop_timeout(self.stop_timeout)

    def set_to_foreground(self):
        if self._run_context is not None:
            self._run_context.reset_stop_timeout()
            self.play_stop_bg_sound(self._last_bg_sound_event_id)

    def step_first(self, time_in_step):
        raise NotImplementedError

    def get_continue_info(self):
        return (self.continue_message, 'Continue', 'Stop')

    def _confirm_step(self):
        Sound.play('clubhouse/dialog/next')
        self._confirmed_step = True
        if self._run_context is not None:
            self._run_context.user_confirmed()

    def confirmed_step(self):
        confirmed = self._confirmed_step
        self._confirmed_step = False
        return confirmed

    def abort(self):
        abort_info = QuestStringCatalog.get_info('{}_ABORT'.format(self._qs_base_id))
        if abort_info:
            self.show_message('ABORT')

        self.pause(5)
        self.stop()

    def stop(self):
        if not self.is_cancelled() and self._cancellable is not None:
            self.play_stop_bg_sound(sound_event_id=None)
            self._cancellable.cancel()

    def get_main_character(self):
        return self._main_character_id

    def play_stop_bg_sound(self, sound_event_id=None):
        """
        Plays an ambient 'bg' sound taking care of stopping the previous sound.

        Warning: If the given sound event id is already playing it will be
        stopped and played back again.
        Args:
            sound_event_id (str): The sound event id of the 'bg' sound.
                                  If `None`, then stop the last bg sound.
        """
        if self._last_bg_sound_uuid:
            Sound.stop(self._last_bg_sound_uuid)
            self._last_bg_sound_uuid = None
            self._last_bg_sound_event_id = None
        if sound_event_id:
            Sound.play(sound_event_id, self._update_last_bg_sound_uuid, sound_event_id)

    def _update_last_bg_sound_uuid(self, _proxy, uuid, sound_event_id):
        if isinstance(uuid, GLib.Error):
            logger.warning('Error when attempting to play sound: %s', uuid.message)
            self._last_bg_sound_uuid = None
            return
        self._last_bg_sound_uuid = uuid
        self._last_bg_sound_event_id = sound_event_id

    def show_message(self, info_id=None, **options):
        if info_id is not None:
            full_info_id = self._qs_base_id + '_' + info_id
            info = QuestStringCatalog.get_info(full_info_id)

            # Fallback to the given info_id if no string was found
            if info is None:
                info = QuestStringCatalog.get_info(info_id)

            options.update(info)

        possible_answers = []
        if options.get('choices'):
            possible_answers = [(text, callback) for text, callback in options['choices']]

        if options.get('use_confirm'):
            confirm_label = options.get('confirm_label', '>')
            possible_answers = [(confirm_label, self._confirm_step)] + possible_answers

        sfx_sound = options.get('sfx_sound')
        if not sfx_sound:
            if info_id == 'ABORT':
                sfx_sound = self._default_abort_sound
            else:
                sfx_sound = self._main_open_dialog_sound
        bg_sound = options.get('bg_sound')

        self._emit_signal('message', options['txt'], possible_answers,
                          options.get('character_id') or self._main_character_id,
                          options.get('mood') or self._main_mood,
                          sfx_sound, bg_sound)

    def _show_next_hint_message(self, info_list, index=0):
        label = "I'd like another hint"
        if index == 0:
            label = "Give me a hint"
        elif index == len(info_list) - 1:
            label = "What's my goal?"

        info_id = info_list[index]
        next_index = (index + 1) % len(info_list)
        next_hint = functools.partial(self._show_next_hint_message, info_list, next_index)
        self.show_message(info_id=info_id, choices=[(label, next_hint)])

    def show_hints_message(self, info_id):
        full_info_id = self._qs_base_id + '_' + info_id
        info_id_list = QuestStringCatalog.get_hint_keys(full_info_id)

        # Fallback to the given info_id if no string was found
        if info_id_list is None:
            full_info_id = info_id
            info_id_list = QuestStringCatalog.get_hint_keys(full_info_id)

        if len(info_id_list) == 1:
            logger.warning('Asked for messages hints, but no hints were found for ID %s; '
                           'not showing the hints button.', info_id)
            self.show_message(info_id)
        else:
            self._show_next_hint_message(info_id_list)

    def get_initial_message(self):
        return self._initial_msg

    def get_last_bg_sound_event_id(self):
        return self._last_bg_sound_uuid

    def give_item(self, item_name, notification_text=None, consume_after_use=False):
        variant = GLib.Variant('a{sb}', {
            'consume_after_use': consume_after_use,
            'used': False
        })
        self.gss.set(item_name, variant)
        self._emit_signal('item-given', item_name, notification_text)

    def complete_current_episode(self):
        current_episode_info = Registry.get_current_episode()
        if current_episode_info['completed']:
            return

        current_episode_info.update({'completed': True})
        self.gss.set('clubhouse.CurrentEpisode', current_episode_info)

    @classmethod
    def give_app_icon(class_, app_name):
        if not Desktop.is_app_in_grid(app_name):
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(app_name)

        Desktop.focus_app(app_name)

    def on_key_event(self, event):
        self.key_event = True

    def debug_skip(self):
        skip = self.key_event or self._debug_skip
        self.key_event = None
        self._debug_skip = False
        return skip

    def set_debug_skip(self, debug_skip):
        self._debug_skip = debug_skip
        if self._run_context is not None:
            self._run_context.debug_dispatch()

    def __repr__(self):
        return self._name

    def _emit_signal(self, signal_name, *args):
        # The quest runs in a separate thread, but we need to emit the
        # signal from the main one
        GLib.idle_add(self.emit, signal_name, *args)

    def set_cancellable(self, cancellable):
        self._cancellable = cancellable

    def get_cancellable(self):
        return self._cancellable

    def is_cancelled(self):
        return self._cancellable is not None and self._cancellable.is_cancelled()

    @classmethod
    def _get_conf_key(class_):
        return class_._get_quest_conf_prefix() + class_.__name__

    @staticmethod
    def _get_quest_conf_prefix():
        return 'quest.'

    def load_conf(self):
        self.conf['complete'] = self.is_named_quest_complete(self.__class__.__name__)

    def save_conf(self):
        key = self._get_conf_key()
        variant = GLib.Variant('a{sb}', {'complete': self.conf['complete']})
        self.gss.set(key, variant)

    def set_conf(self, key, value):
        self.conf[key] = value

    def get_conf(self, key):
        return self.conf.get(key)

    def dismiss(self):
        self._emit_signal('dismissed')

    def is_named_quest_complete(self, class_name):
        key = self._get_quest_conf_prefix() + class_name
        data = self.gss.get(key)
        return data is not None and data['complete']

    def _get_available(self):
        return self._available

    def _set_available(self, value):
        if self._available == value:
            return
        self._available = value
        self.notify('available')

    def with_app_launched(app_name, otherwise='abort'):
        def wrapper(func):
            app = App(app_name)

            def wrapped_func(instance, *args):
                app_quit_callback = getattr(instance, otherwise)
                app_was_quit = False
                handler_id = 0

                if not app.is_running():
                    return app_quit_callback

                def _app_running_changed(app, instance, app_quit_callback):
                    nonlocal app_was_quit

                    if not app.is_running():
                        app.disconnect_running_change(handler_id)
                        app_was_quit = True
                        app_quit_callback()

                # Check if the app is quit while the wrapped function is being run
                # if so, we run the alternative callback instead
                handler_id = app.connect_running_change(_app_running_changed, app,
                                                        instance, app_quit_callback)

                ret = func(instance, *args)

                if app_was_quit:
                    return None

                # We only disconnect here if the app wasn't quit
                app.disconnect_running_change(handler_id)
                return ret

            return wrapped_func

        return wrapper

    @classmethod
    def get_id(class_):
        return class_.__name__

    available = GObject.Property(_get_available, _set_available, type=bool, default=True,
                                 flags=GObject.ParamFlags.READWRITE |
                                 GObject.ParamFlags.EXPLICIT_NOTIFY)


class QuestSet(GObject.GObject):

    __quests__ = []
    # @todo: Default character; should be set to None in the future
    __character_id__ = 'aggretsuko'
    __position__ = (0, 0)
    __empty_message__ = 'Nothing to see here!'

    visible = GObject.Property(type=bool, default=True)
    highlighted = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()
        self._position = self.__position__

        self._quest_objs = []
        for quest_class in self.__quests__:
            quest = quest_class()
            self._quest_objs.append(quest)
            quest.connect('notify',
                          lambda quest, param: self.on_quest_properties_changed(quest, param.name))
            quest.connect('dismissed', self._update_highlighted)

        self._update_highlighted()

    @classmethod
    def get_character(class_):
        return class_.__character_id__

    def get_quests(self):
        return self._quest_objs

    @classmethod
    def get_id(class_):
        return class_.__name__

    def __repr__(self):
        return self.get_id()

    def get_next_quest(self):
        for quest in self.get_quests():
            if not quest.conf['complete']:
                if quest.available:
                    return quest
                if not quest.skippable:
                    break
        return None

    def get_empty_message(self):
        return self.__empty_message__

    def get_position(self):
        return self._position

    def _update_highlighted(self, _current_quest=None):
        next_quest = self.get_next_quest()
        self.highlighted = next_quest is not None and next_quest.available
        if self.highlighted:
            logger.info('QuestSet "%s" highlighted by quest %s', self, next_quest)
        else:
            logger.info('QuestSet "%s" highlight removed', self)

    def on_quest_properties_changed(self, quest, prop_name):
        logger.debug('Quest "%s" property changed: %s', quest, prop_name)
        if prop_name == 'available' and quest.get_property(prop_name):
            if not self.visible:
                logger.info('Turning QuestSet "%s" visible from quest %s', self, quest)
                self.visible = True
            if self.get_next_quest() == quest:
                logger.info('QuestSet "%s" highlighted by new available quest %s', self, quest)
                self.highlighted = True

    def is_active(self):
        return self.visible and self.get_next_quest() is not None
