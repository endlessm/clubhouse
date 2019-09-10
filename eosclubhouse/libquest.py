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

from collections import OrderedDict
from enum import Enum, IntEnum
from eosclubhouse import config, logger
from eosclubhouse.system import App, Desktop, GameStateService, Sound
from eosclubhouse.utils import get_alternative_quests_dir, ClubhouseState, MessageTemplate, \
    Performance, QuestStringCatalog, QS, convert_variant_arg
from gi.repository import GObject, GLib


# Set up the asyncio loop implementation
glibcoro.install()


DEFAULT_CHARACTER = 'ada'


class Registry:

    _quest_sets_to_register = []
    _quest_sets = []
    _quest_instances = {}
    _loaded_modules = set()
    _loaded_episode = None
    _autorun_quest = None

    @classmethod
    def set_episode_required_state(class_, quest_folder):
        basedir = os.path.dirname(quest_folder)
        sys.path.append(basedir)

        basename = os.path.basename(quest_folder)
        try:
            module = __import__(basename)
        except ImportError:
            # This may mean that the quest folder is not a package, which is fine.
            pass
        else:
            set_required_game_state = getattr(module, 'set_required_game_state', None)
            if callable(set_required_game_state):
                set_required_game_state()

        del sys.path[sys.path.index(basedir)]

    @classmethod
    @Performance.timeit
    def load(class_, quest_folder):
        parent_dir = os.path.dirname(quest_folder)
        if parent_dir in sys.path:
            parent_dir = None
        else:
            sys.path.append(parent_dir)

        for _unused, modname, _unused in pkgutil.walk_packages([quest_folder]):
            # Import the module with the episode name as its prefix to make sure we use the right
            # quests when included them by name (without the episode prefix, we could end up
            # including a quest that is not the right one if there are two quests with the same
            # name across episodes that have been loaded).
            module_with_episode = os.path.basename(quest_folder) + '.' + modname
            __import__(module_with_episode)
            class_._loaded_modules.add(module_with_episode)

        for quest_set_class in class_._quest_sets_to_register:
            class_._quest_sets.append(quest_set_class())
            logger.debug('QuestSet registered: %s', quest_set_class)

        if parent_dir is not None:
            del sys.path[sys.path.index(parent_dir)]
        class_._quest_sets_to_register = []

    @classmethod
    def _reset(class_):
        class_._loaded_episode = None
        class_._autorun_quest = None
        class_._quest_sets_to_register = []
        class_._quest_sets = []
        class_._quest_instances = {}
        for module in class_._loaded_modules:
            del sys.modules[module]
        class_._loaded_modules = set()

    @classmethod
    @Performance.timeit
    def register_quest_set(class_, quest_set):
        if not issubclass(quest_set, QuestSet):
            raise TypeError('{} is not a of type {}'.format(quest_set, QuestSet))
        class_._quest_sets_to_register.append(quest_set)

    @classmethod
    def get_quest_sets(class_):
        return class_._quest_sets

    @classmethod
    def get_character_missions(class_):
        return [q for q in class_._quest_sets if isinstance(q, CharacterMission)]

    @classmethod
    def get_character_mission_for_character(class_, character_id):
        for qs in class_.get_character_missions():
            if qs.get_character() == character_id:
                return qs
        return None

    @classmethod
    def get_character_mission_for_quest(class_, quest):
        # Note: this assumes that the character missions don't share
        # quests. If not, it will return the first mission matching.
        for qs in class_.get_character_missions():
            if quest in qs.get_quests():
                return qs
        return None

    @classmethod
    def get_pathways(class_):
        return [q for q in class_._quest_sets if isinstance(q, PathWay)]

    @classmethod
    def get_quest_set_by_name(class_, name):
        for quest_set in class_.get_quest_sets():
            if quest_set.get_id() == name:
                return quest_set

        return None

    @classmethod
    def has_quest_sets_highlighted(class_):
        return any(qs.highlighted for qs in class_.get_character_missions())

    @classmethod
    def get_quest_by_name(class_, name):
        quest_set_name = None
        name_split = name.split('.', 1)

        if len(name_split) > 1:
            quest_set_name, quest_name = name_split
        else:
            quest_name = name

        return class_.get_current_quests().get(quest_name)

    @classmethod
    def _get_episode_folder(class_, episode_name):
        return os.path.join(os.path.dirname(__file__), 'quests', episode_name)

    @staticmethod
    def _get_episode_module(episode_folder):
        basedir = os.path.dirname(episode_folder)
        sys.path.append(basedir)

        basename = os.path.basename(episode_folder)
        module = None

        try:
            module = __import__(basename)
        except ImportError:
            # This may mean that the quest folder is not a package, which is fine.
            pass

        del sys.path[sys.path.index(basedir)]

        return module

    @classmethod
    def load_current_episode(class_):
        loaded_episodes = {}
        episode_name = class_.get_current_episode()['name']

        # We keep loading the current episode until it's not been changed after loading it.
        # This avoids having a quest set a new episode when it's loaded but we'd thus end up
        # with an old episode loaded.
        while class_._loaded_episode != episode_name:
            logger.info('Loading episode %s', episode_name)

            class_._reset()

            class_._loaded_episode = episode_name

            episode_folder = class_._get_episode_folder(episode_name)

            module = class_._get_episode_module(episode_folder)
            if module:
                class_._autorun_quest = getattr(module, 'AUTORUN_QUEST', None)

            class_.load(episode_folder)

            # Avoid circular episode setting (a quest setting an episode that when loaded
            # sets a previously loaded episode)
            if episode_name in loaded_episodes:
                logger.warning('Episode "%s" has already been loaded by %s! This means there is a '
                               'circular setting of episodes!', episode_name,
                               loaded_episodes[episode_name])
                break

            loaded_episodes[episode_name] = class_._loaded_episode
            episode_name = class_.get_current_episode()['name']

        class_.load(get_alternative_quests_dir())

    @classmethod
    def get_loaded_episode_name(class_):
        return class_._loaded_episode

    @classmethod
    def get_current_quests(class_):
        quest_sets = class_.get_quest_sets()
        quests_dict = OrderedDict()
        for quest_set in quest_sets:
            for quest in quest_set.get_quests():
                quests_dict[quest.get_id()] = quest
        return quests_dict

    @classmethod
    def get_current_episode_progress(class_):
        all_quests = class_.get_current_quests().values()
        complete_quests = len(list(filter(lambda quest: quest.complete, all_quests)))
        return complete_quests / len(all_quests)

    @classmethod
    def get_autorun_quest(class_):
        return class_._autorun_quest

    @classmethod
    def get_available_episodes(class_):
        episodes_path = os.path.join(os.path.dirname(__file__), 'quests')
        episodes = os.listdir(episodes_path)
        # Exclude paths that are special to Python (they usually start with __).
        return (e for e in episodes if os.path.isdir(os.path.join(episodes_path, e)) and not
                e.startswith('__'))

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
    def set_current_episode(class_, episode_name, force=False):
        if episode_name not in class_.get_available_episodes():
            raise KeyError
        if not force and episode_name == class_.get_current_episode()['name']:
            return

        episode_folder = class_._get_episode_folder(episode_name)
        class_.set_episode_required_state(episode_folder)

        logger.debug('Setting episode: %s', episode_name)
        episode_info = {'name': episode_name, 'completed': False, 'teaser-viewed': False}
        GameStateService().set('clubhouse.CurrentEpisode', episode_info)

    @classmethod
    def set_current_episode_teaser_viewed(class_, viewed):
        current_episode_info = class_.get_current_episode()
        if not current_episode_info['completed']:
            return

        current_episode_info.update({'teaser-viewed': viewed})
        GameStateService().set('clubhouse.CurrentEpisode', current_episode_info)

    @classmethod
    def _get_episode_quests_classes(class_):
        current_episode = class_.get_loaded_episode_name()
        for subclass in Quest.__subclasses__():
            # Avoid matching subclasses with the same name but in different episodes
            episode = subclass.__module__.split('.', 1)[0]
            if episode != current_episode:
                continue
            yield subclass

    @classmethod
    def get_matching_quests(class_, tag):
        for subclass in class_._get_episode_quests_classes():
            if tag in subclass.get_tags():
                if subclass not in class_._quest_instances:
                    class_._quest_instances[subclass] = subclass()
                yield class_._quest_instances[subclass]

    @classmethod
    def get_quest_class_by_name(class_, name):
        for subclass in class_._get_episode_quests_classes():
            if subclass.__name__ == name:
                return subclass

        raise TypeError('Quest {} not found'.format(name))


class _QuestRunContext:

    def __init__(self, cancellable):
        self._confirm_action = None

        asyncio.set_event_loop(asyncio.new_event_loop())

        self._step_loop = asyncio.new_event_loop()
        self._timeout_handle = None
        self._cancellable = cancellable
        self._debug_actions = set()
        self._current_waiting_loop = None

    def _cancel_and_close_loop(self, loop):
        if not loop.is_closed():
            for task in asyncio.Task.all_tasks(loop=loop):
                task.cancel()

            loop.stop()
            loop.close()

    def _cancel_all(self):
        self.reset_stop_timeout()

        if self._current_waiting_loop is not None:
            self._cancel_and_close_loop(self._current_waiting_loop)

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
            logger.debug('Executing step: %s%r', step_func.__name__, args_)
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

        pause_handler = None

        def _cancel_pause():
            if pause_handler is not None:
                pause_handler.cancel()

        cancel_handler_id = self._cancellable.connect(_cancel_pause)

        def _pause_finished():
            async_action.resolve()

            nonlocal cancel_handler_id
            if cancel_handler_id > 0:
                self._cancellable.disconnect(cancel_handler_id)
            cancel_handler_id = 0

        loop = self._future_get_loop(async_action.future)
        pause_handler = loop.call_later(secs, _pause_finished)

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

        self._current_waiting_loop = loop = asyncio.new_event_loop()

        loop.run_until_complete(wait_or_timeout(futures, timeout))
        loop.stop()
        loop.close()

        self._current_waiting_loop = None

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

    def resolve(self, result=True):
        if self.future is not None and not self.future.done():
            self.future.set_result(result)

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


class NoMessageIdError(Exception):
    pass


class _Quest(GObject.GObject):

    Difficulty = IntEnum('Difficulty', ['EASY', 'NORMAL', 'HARD'])
    DEFAULT_DIFFICULTY = Difficulty.NORMAL
    MessageType = Enum('MessageType', ['POPUP', 'NARRATIVE'])

    __gsignals__ = {
        'quest-started': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
        'quest-finished': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
        'message': (
            GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)
        ),
        'dismiss-message': (
            GObject.SignalFlags.RUN_FIRST, None, (bool,)
        ),
        'item-given': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str)
        ),
        'dismissed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
        'schedule-quest': (
            GObject.SignalFlags.RUN_FIRST, None, (str, bool, int)
        ),
    }

    __sound_on_run_begin__ = 'quests/quest-given'
    # @todo: Is this still relevant?
    __available_after_completing_quests__ = []
    # Should be in the form 'key': {...} , a dict of the key's content, or an empty dict for
    # using the default key's content.
    __items_on_completion__ = {}
    __conf_on_completion__ = {}
    __proposal_message_id__ = 'QUESTION'

    _DEFAULT_TIMEOUT = 2 * 3600  # secs
    _DEFAULT_MOOD = 'talk'

    __quest_name__ = None
    __tags__ = []
    __mission_order__ = 0
    __pathway_order__ = 0

    __is_narrative__ = False

    __auto_offer_info__ = {'confirm_before': True, 'start_after': 3}

    skippable = GObject.Property(type=bool, default=False)
    stop_timeout = GObject.Property(type=int, default=_DEFAULT_TIMEOUT)
    continue_message = GObject.Property(type=str, default="You haven't completed my challenge yet!")
    proposal_message = GObject.Property(type=str, default="Do you want to go for a challenge?")
    proposal_mood = GObject.Property(type=str, default=_DEFAULT_MOOD)
    proposal_sound = GObject.Property(type=str, default="quests/quest-proposed")

    _labels = {
        'QUEST_ACCEPT': 'Sure!',
        'QUEST_REJECT': 'Not now…',
        'QUEST_ACCEPT_STOP': 'Yes',
        'QUEST_REJECT_STOP': 'No',
        'QUEST_ACCEPT_HARDER': 'Yes',
        'QUEST_REJECT_HARDER': 'No',
    }

    stopping = GObject.Property(type=bool, default=False)

    auto_offer = GObject.Property(type=bool, default=False)

    def __init__(self):
        super().__init__()

        # We declare these variables here, instead of looking them up in the registry when
        # we need them because this way we ensure we get the values when the quest was loaded,
        # and eventually prevent situations where the quest uses these values from the Registry
        # but meanwhile a new episode has been loaded (unlikely, but disastrous if it happens).
        self._episode_name = Registry.get_loaded_episode_name()

        self._qs_base_id = self.get_default_qs_base_id()

        self._last_bg_sound_uuid = None
        self._last_bg_sound_event_id = None

        self._characters = {}

        self._main_character_id = DEFAULT_CHARACTER
        self._main_mood = self._DEFAULT_MOOD
        self._main_open_dialog_sound = 'clubhouse/dialog/open'
        self._default_abort_sound = 'quests/quest-aborted'

        self._setup_proposal_message()
        self._setup_labels()

        self.gss = GameStateService()
        self.conf = {}
        self.load_conf()

        self._highlighted = False
        self._available = self.__available_after_completing_quests__ == []
        if self.__available_after_completing_quests__ != []:
            self.gss.connect('changed', self.update_availability)
            self.update_availability()

        self._cancellable = None

        self.key_event = False
        self._debug_skip = False

        self._confirmed_step = False

        self._toolbox_topic_clicked = None

        self._run_context = None

        self.reset_hints_given_once()

        self.clubhouse_state = ClubhouseState()

        self.setup()

    def setup(self):
        '''Initialize/setup anything that is related to the quest implementation

        Instead of having to define a constructor, subclasses of Quest should set up anything
        related to their construction in this method. This way Quest implementations should
        only define a constructor when needed, which simplifies the quests making them more
        readable.

        This method is called just once (in the Quest's base constructor). Code that needs
        to be called on every quest run, should be added to the `step_begin` method.
        '''
        pass

    def _get_message_info(self, message_id):
        message_info = QuestStringCatalog.get_info(message_id)

        if message_info is None:
            return None

        if MessageTemplate.delimiter in message_info['txt']:
            message_variables = self._get_message_variables()
            message_template = MessageTemplate(message_info['txt'])
            parsed_text = message_template.substitute(message_variables)
            message_info['parsed_text'] = parsed_text
        else:
            message_info['parsed_text'] = message_info['txt']

        return message_info

    def _setup_proposal_message(self):
        message_id = self.__proposal_message_id__
        message_info = self._get_message_info('{}_{}'.format(self._qs_base_id, message_id))

        if message_info is None:
            logger.debug('Proposal message %r is missing for quest %r',
                         message_id, self._qs_base_id)
            return

        self.proposal_message = message_info['parsed_text']
        sfx_sound = message_info.get('sfx_sound')
        if sfx_sound:
            self.proposal_sound = sfx_sound

        character_id = message_info.get('character_id')
        if character_id:
            self._main_character_id = character_id

        mood = message_info.get('mood')
        if mood:
            self.proposal_mood = mood

    def _setup_labels(self):
        for message_id in self._labels:
            label = QS('{}_{}'.format(self._qs_base_id, message_id))
            if label:
                self._labels[message_id] = label

    def get_label(self, message_id):
        return self._labels[message_id]

    def get_episode_name(self):
        return self._episode_name

    def update_availability(self, _gss=None):
        if self.complete:
            return
        if all(self.is_named_quest_complete(q)
               for q in self.__available_after_completing_quests__):
            self.available = True

    def get_default_qs_base_id(self):
        return str(self.__class__.__name__).upper()

    def run(self, on_quest_finished):
        assert hasattr(self, 'step_begin'), ('Quests need to declare a "step_begin" method, in '
                                             'order to be run.')
        self.run_in_context(on_quest_finished)

    def run_in_context(self, quest_finished_cb):
        if self.__sound_on_run_begin__:
            Sound.play(self.__sound_on_run_begin__)

        # Reset the "stopping" property before running the quest.
        self.stopping = False

        # Reset the hints given once:
        self.reset_hints_given_once()

        self._run_context = _QuestRunContext(self._cancellable)
        self.emit('quest-started')
        self._run_context.run(self.step_begin)
        self._run_context = None

        self.run_finished()
        quest_finished_cb(self)
        self.emit('quest-finished')

        # The quest is stopped, so reset the "stopping" property again.
        self.stopping = False

    def run_finished(self):
        """This method is called when a quest finishes running.

        It can be overridden when quests need to run logic associated with that moment. By default
        it schedules the next quest to be run (if there's any).
        """

        # Only try to propose the next quest if this one is complete.
        if not self.complete:
            return

        next_quest = self.get_next_auto_offer_quest()
        if next_quest:
            logger.debug('Proposing next quest: %s', next_quest)
            self.schedule_quest(next_quest.get_id(), **next_quest.get_auto_offer_info())

    def set_next_step(self, step_func, delay=0, args=()):
        assert self._run_context is not None
        self._run_context.set_next_step(step_func, delay, args)

    def ask_for_app_launch(self, app, timeout=None, pause_after_launch=2, message_id='LAUNCH',
                           give_app_icon=True):
        if app.is_running() or self.is_cancelled():
            return

        if message_id is not None:
            self.show_hints_message(message_id)

        if give_app_icon:
            self.give_app_icon(app.dbus_name)

        self.wait_for_app_launch(app, timeout=timeout, pause_after_launch=pause_after_launch)

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

    def connect_app_object_props_changes(self, app, obj, props):
        assert len(props) > 0
        return self._connect_app_changes(app, obj, props)

    def connect_app_js_props_changes(self, app, props):
        return self.connect_app_object_props_changes(app, app.APP_JS_PARAMS, props)

    def connect_app_quit(self, app):
        return self._connect_app_changes(app, None, [])

    def connect_app_props_changes(self, app, props):
        return self._connect_app_changes(app, None, props)

    def _connect_app_changes(self, app, obj, props):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()

        def _on_app_running_changed(app, async_action):
            if not app.is_running() and not async_action.is_resolved():
                async_action.resolve()

        running_handler_id = 0
        props_handlers = []

        def _disconnect_app(_future):
            for handler_id in props_handlers:
                app.disconnect_object_props_change(handler_id)

            app.disconnect_running_change(running_handler_id)

        if not app.is_running():
            async_action.cancel()

        if async_action.is_cancelled():
            return async_action

        async_action.future.add_done_callback(_disconnect_app)

        if len(props) > 0:
            try:
                props_handlers = app.connect_props_change(obj, props,
                                                          lambda: async_action.resolve())
            except GLib.Error as e:
                # Prevent any D-Bus errors (like ServiceUnknown when the app has been quit)
                logger.debug('Could not connect to app "%s" object property changes: %s',
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

    def connect_clubhouse_changes(self, props_list):
        assert self._run_context is not None

        state = ClubhouseState()
        async_action = self._run_context.new_async_action()
        if async_action.is_cancelled():
            return async_action

        property_handler_id = 0

        def _disconnect_clubhouse(_future=None):
            nonlocal property_handler_id
            nonlocal state
            if property_handler_id > 0:
                state.disconnect(property_handler_id)
                property_handler_id = 0

        def _on_property_changed(property_name):
            nonlocal props_list
            if property_name in props_list:
                _disconnect_clubhouse()
                async_action.resolve()

        async_action.future.add_done_callback(_disconnect_clubhouse)

        property_handler_id = state.connect('notify', lambda state, param:
                                            _on_property_changed(param.name))

        return async_action

    def connect_toolbox_topic_clicked(self, toolbox_topic):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()
        if async_action.is_cancelled():
            return async_action

        clicked_handler_id = 0

        def _disconnect_clicked(_future):
            nonlocal clicked_handler_id
            nonlocal toolbox_topic
            if clicked_handler_id > 0:
                toolbox_topic.disconnect_clicked(clicked_handler_id)
                clicked_handler_id = 0

        def _on_clicked_cb(app_name, topic_name):
            self._toolbox_topic_clicked = {'app': app_name, 'topic': topic_name}
            async_action.resolve()

        async_action.future.add_done_callback(_disconnect_clicked)

        clicked_handler_id = toolbox_topic.connect_clicked(_on_clicked_cb)

        return async_action

    def pause(self, secs):
        assert self._run_context is not None
        return self._run_context.pause(secs)

    def wait_confirm(self, msg_id=None, timeout=None, **options):
        return self.show_confirm_message(msg_id, **options).wait(timeout)

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

    def show_choices_message(self, msg_id, *user_choices, **options):
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()

        if async_action.is_cancelled():
            return async_action

        def _callback_and_resolve(async_action, callback, *callback_args):
            ret = callback(*callback_args)
            async_action.resolve(ret)

        choices = options.get('choices', [])
        for option_msg_id, callback, *args in user_choices:
            option_label = QS('{}_{}'.format(self._qs_base_id, option_msg_id))
            choices.append((option_label, _callback_and_resolve, async_action, callback, *args))

        options.update({'choices': choices})
        self.show_message(msg_id, **options)

        return async_action

    def wait_for_one(self, action_list, timeout=None):
        self._run_context.wait_for_one(action_list, timeout)

    def set_to_background(self):
        if self._run_context is not None:
            if self._last_bg_sound_uuid:
                Sound.stop(self._last_bg_sound_uuid)
                self._last_bg_sound_uuid = None
            self._run_context.run_stop_timeout(self.stop_timeout)

            # If we are stopping already, then call stop() right away because the quest is no
            # longer visible.
            if self.stopping:
                self.stop()

    def set_to_foreground(self):
        if self._run_context is not None:
            self._run_context.reset_stop_timeout()
            self.play_stop_bg_sound(self._last_bg_sound_event_id)

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

    def toolbox_topic_clicked(self):
        toolbox_topic_clicked = self._toolbox_topic_clicked
        self._toolbox_topic_clicked = None
        return toolbox_topic_clicked

    def abort(self):
        if self.stopping:
            return

        # Notify we're going to stop soon
        self.stopping = True

        abort_info = self._get_message_info('{}_ABORT'.format(self._qs_base_id))
        if abort_info:
            self.show_message('ABORT')
            self.pause(5)
        else:
            Sound.play(self._default_abort_sound)

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

    def _get_message_variables(self):
        return {'user_name': GLib.get_real_name()}

    def show_message(self, info_id=None, **options):
        if info_id is not None:
            full_info_id = self._qs_base_id + '_' + info_id
            info = self._get_message_info(full_info_id)

            # Fallback to the given info_id if no string was found
            if info is None:
                info = self._get_message_info(info_id)
            else:
                info_id = full_info_id

            if info is None:
                raise NoMessageIdError("Can't show message, the message ID " + info_id +
                                       " is not in the catalog.")

            options.update(info)

        if options.get('narrative', False):
            message_type = self.MessageType.NARRATIVE
        else:
            message_type = self.MessageType.POPUP

        if not self.is_narrative() and message_type == self.MessageType.NARRATIVE:
            logger.warning('Can\'t show message %r, quest %r is not narrative.', info_id, self)
            return

        possible_answers = []
        if options.get('choices'):
            possible_answers = [(text, callback, *args)
                                for text, callback, *args
                                in options['choices']]

        if options.get('use_confirm'):
            confirm_label = options.get('confirm_label', '>')
            possible_answers = [(confirm_label, self._confirm_step)] + possible_answers

        sfx_sound = options.get('sfx_sound')
        if not sfx_sound:
            if info_id == 'ABORT':
                sfx_sound = self._default_abort_sound
            elif info_id == 'QUESTION':
                sfx_sound = self.proposal_sound
            else:
                sfx_sound = self._main_open_dialog_sound
        bg_sound = options.get('bg_sound')

        self.emit('message', {
            'id': info_id,
            'text': options['parsed_text'],
            'choices': possible_answers,
            'character_id': options.get('character_id') or self.get_main_character(),
            'character_mood': options.get('mood') or self._main_mood,
            'sound_fx': sfx_sound,
            'sound_bg': bg_sound,
            'type': message_type,
        })

    def dismiss_message(self, narrative=False):
        self.emit('dismiss-message', narrative)

    def reset_hints_given_once(self):
        self._hints_given_once = set()

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

    def show_hints_message(self, info_id, give_once=False):
        if give_once:
            if info_id in self._hints_given_once:
                return
            else:
                self._hints_given_once.add(info_id)

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

    @classmethod
    def highlight_quest(self, quest_name):
        other_quest = Registry.get_quest_by_name(quest_name)
        if other_quest:
            other_quest.props.highlighted = True

    def get_last_bg_sound_event_id(self):
        return self._last_bg_sound_uuid

    def give_item(self, item_name, notification_text=None, consume_after_use=False,
                  optional=False):
        if not optional:
            assert item_name in self.__items_on_completion__, \
                ("The item {} is not being given as optional and it is not declared in the "
                 "quest's __items_on_completion__!".format(item_name))

        if self.is_cancelled():
            logger.debug('Not giving item "%s" because the quest has been cancelled.', item_name)
            return

        self._set_item(item_name, {'consume_after_use': consume_after_use})
        self.emit('item-given', item_name, notification_text)

    def _set_item(self, item_name, extra_info={}, skip_if_exists=False):
        current_state = self.gss.get(item_name)
        if current_state is not None:
            if skip_if_exists:
                return
            if current_state.get('used', False):
                logger.warning('Attempt to give item %s failed, it was already given and used',
                               item_name)
                return

        info = {'consume_after_use': False,
                'used': False}
        info.update(extra_info)

        self.gss.set(item_name, GLib.Variant('a{sb}', info))

    def is_panel_unlocked(self, lock_id):
        lock_state = self.gss.get(lock_id)
        return lock_state is not None and not lock_state.get('locked', True)

    def schedule_quest(self, quest_name, confirm_before=True, start_after=3):
        self.emit('schedule-quest', quest_name, confirm_before, start_after)

    @classmethod
    def get_pathways(class_):
        quest_pathways = []
        registered_pathways = Registry.get_pathways()
        for tag in class_.get_tags():
            if not tag.startswith('pathway:'):
                continue
            pathway_name = tag.split(':')[1].lower()
            try:
                pathway = \
                    next(p for p in registered_pathways if p.get_name().lower() == pathway_name)
                quest_pathways.append(pathway)
            except StopIteration:
                continue
        return quest_pathways

    @classmethod
    def get_name(class_):
        if class_.__quest_name__ is not None:
            return class_.__quest_name__

        # Fallback to the class name:
        logger.warning('The quest "%s" doesn\'t have a name!', class_)
        return class_.__name__

    @classmethod
    def get_tags(class_):
        return class_.__tags__

    @classmethod
    def get_auto_offer_info(class_):
        return class_.__auto_offer_info__

    @classmethod
    def get_difficulty(class_):
        for tag in class_.get_tags():
            if not tag.startswith('difficulty:'):
                continue

            difficulty = tag.split(':')[1].upper()
            try:
                return getattr(class_.Difficulty, difficulty)
            except AttributeError:
                continue

        return class_.DEFAULT_DIFFICULTY

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
        return self.get_id()

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
        key = self._get_conf_key()
        self.conf = self.gss.get(key, value_if_missing={})
        self.complete = self.conf.get('complete', False)

    def get_complete(self):
        return self.conf['complete']

    def _get_complete(self):
        return self.get_complete()

    def set_complete(self, is_complete):
        self.conf['complete'] = is_complete

    def _set_complete(self, is_complete):
        self.set_complete(is_complete)

    def _get_highlighted(self):
        return self._highlighted

    def _set_highlighted(self, is_highlighted):
        if self._highlighted == is_highlighted:
            return
        self._highlighted = is_highlighted
        self.notify('highlighted')

    def save_conf(self):
        conf_key = self._get_conf_key()
        for key, value in self.conf.items():
            variant = convert_variant_arg({key: value})
            self.gss.set_async(conf_key, variant)

        if self.complete:
            for item_id, extra_info in self.__items_on_completion__.items():
                self._set_item(item_id, extra_info, skip_if_exists=True)

            for item_id, info in self.__conf_on_completion__.items():
                self.gss.set(item_id, info)

    def set_conf(self, key, value):
        self.conf[key] = value

    def get_conf(self, key):
        return self.conf.get(key)

    def dismiss(self):
        self.emit('dismissed')

    def get_named_quest_conf(self, class_name, key):
        gss_key = self._get_quest_conf_prefix() + class_name
        data = self.gss.get(gss_key)

        if data is None:
            return None
        return data.get(key)

    def is_named_quest_complete(self, class_name):
        data = self.get_named_quest_conf(class_name, 'complete')
        return data is not None and data

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

    def get_next_auto_offer_quest(self):
        for quest_set in Registry.get_quest_sets():
            quest = quest_set.get_next_quest()
            if quest and quest is not self and quest.auto_offer:
                return quest

        return None

    def highlight_character(self, character_id=None):
        if character_id is not None:
            character_mission = Registry.get_character_mission_for_character(character_id)
            if character_mission is None:
                logger.warning('Quest "%s" is trying to highlight character "%s", but there is'
                               ' no such character mission.', self, character_id)
                return

        else:
            character_mission = Registry.get_character_mission_for_quest(self)
            if character_mission is None:
                logger.warning('Quest "%s" is trying to highlight a character, but it doesn\'t'
                               ' belong to any character mission.', self)
                return

        character_mission.highlighted = True

    @classmethod
    def is_narrative(class_):
        return class_.__is_narrative__

    @classmethod
    def get_id(class_):
        return class_.__name__

    available = GObject.Property(_get_available, _set_available, type=bool, default=True,
                                 flags=GObject.ParamFlags.READWRITE |
                                 GObject.ParamFlags.EXPLICIT_NOTIFY)

    complete = GObject.Property(_get_complete, _set_complete, type=bool, default=False,
                                flags=GObject.ParamFlags.READWRITE |
                                GObject.ParamFlags.EXPLICIT_NOTIFY)
    highlighted = GObject.Property(_get_highlighted, _set_highlighted, type=bool, default=False,
                                   flags=GObject.ParamFlags.READWRITE |
                                   GObject.ParamFlags.EXPLICIT_NOTIFY)


class Quest(_Quest):
    '''Hack Quests are written by subclassing this class.

    - Define your quest using attributes like :attr:`__tags__` below.
    - Write a :meth:`step_begin()` method.
    - Build the flow of steps by returning the name of the next step from steps.
    - Finish by returning :meth:`step_complete_and_stop()` from a step.
    '''

    def __init__(self):
        super().__init__()


class QuestSet(GObject.GObject):

    __quests__ = []

    def __init__(self):
        super().__init__()

        self._quest_objs = []

        tag = self.get_tag()
        for quest in Registry.get_matching_quests(tag):
            self._quest_objs.append(quest)

        # @todo: Remove old behavior.
        for quest_class in self.__quests__:
            if isinstance(quest_class, str):
                quest_class = Registry.get_quest_class_by_name(quest_class)
            quest = quest_class()

            self._quest_objs.append(quest)

        self._sort_quests()

    @classmethod
    def get_tag(class_):
        # @todo: This should be only implemented in the subclasses,
        # but leaving here for now to make the tests pass.
        return ''

    def _sort_quests(self):
        # @todo: This should be only implemented in the subclasses,
        # but leaving here for now to make the tests pass.
        self._quest_objs.sort()

    @classmethod
    def get_id(class_):
        return class_.__name__

    def get_quests(self, also_skippable=True):
        if also_skippable:
            return self._quest_objs
        return [q for q in self._quest_objs if not q.skippable]

    # @todo: Remove this by moving all uses of QuestSet to
    # CharacterMission.
    def is_active(self):
        return False

    # @todo: Remove this by moving all uses of QuestSet to
    # CharacterMission.
    def get_next_quest(self):
        return None

    def __repr__(self):
        return self.get_id()


class PathWay(QuestSet):

    __pathway_name__ = None

    def __init__(self):
        super().__init__()

    @classmethod
    def get_tag(class_):
        return 'pathway:' + class_.__pathway_name__.lower()

    @classmethod
    def get_name(class_):
        return class_.__pathway_name__

    def _sort_quests(self):
        def by_order(quest):
            return quest.__pathway_order__

        self._quest_objs.sort(key=by_order)


class CharacterMission(QuestSet):

    __character_id__ = None
    __empty_message__ = 'Nothing to see here!'

    visible = GObject.Property(type=bool, default=True)

    def __init__(self):
        super().__init__()
        self._highlighted = False

        for quest in self.get_quests():
            quest.connect('notify',
                          lambda quest, param: self.on_quest_properties_changed(quest, param.name))

    @classmethod
    def get_tag(class_):
        return 'mission:' + class_.__character_id__.lower()

    def _sort_quests(self):
        def by_order(quest):
            return quest.__mission_order__

        self._quest_objs.sort(key=by_order)

    @classmethod
    def get_character(class_):
        return class_.__character_id__

    def get_next_quest(self):
        for quest in self.get_quests():
            if not quest.conf['complete']:
                if quest.available:
                    return quest
                if not quest.skippable:
                    break
        return None

    def _get_highlighted(self):
        return self._highlighted

    def _set_highlighted(self, highlighted):
        self._highlighted = highlighted

    def on_quest_properties_changed(self, quest, prop_name):
        logger.debug('Quest "%s" property changed: %s', quest, prop_name)
        if prop_name == 'available' and quest.get_property(prop_name):
            if not self.visible:
                logger.debug('Turning QuestSet "%s" visible from quest %s', self, quest)
                self.visible = True
            if self.get_next_quest() == quest:
                logger.debug('QuestSet "%s" highlighted by new available quest %s', self, quest)
                self.highlighted = True

    def is_active(self):
        return self.visible and self.get_next_quest() is not None

    def get_empty_message(self):
        msg_id_suffix = None
        character_id = self.get_character()
        string_info = None

        def get_noquest_message(msg_id_suffix):
            msg_id_suffix = msg_id_suffix.upper()

            # Try to get the NOQUEST message with the episode prefix, otherwise default to the
            # generic one.
            episode_name = Registry.get_loaded_episode_name()
            full_message_id = 'NOQUEST_{}_{}'.format(episode_name.upper(), msg_id_suffix)
            message_info = QuestStringCatalog.get_info(full_message_id)

            if message_info is not None:
                return message_info

            return QuestStringCatalog.get_info('NOQUEST_' + msg_id_suffix)

        for quest_set in Registry.get_quest_sets():
            if quest_set is self:
                continue

            if quest_set.is_active():
                msg_id_suffix = '{}_{}'.format(character_id, quest_set.get_character())

                string_info = get_noquest_message(msg_id_suffix)
                if string_info is not None:
                    break

        if string_info is None:
            msg_id_suffix = '{}_NOTHING'.format(character_id)
            string_info = get_noquest_message(msg_id_suffix)

            if string_info is None:
                return self.__empty_message__

        return string_info['txt']

    def get_easier_quest(self, quest):
        if quest.complete:
            return None

        for q in self.get_quests(also_skippable=False):
            if not q.complete and q.get_difficulty() < quest.get_difficulty():
                return q

        return None

    highlighted = GObject.Property(_get_highlighted, _set_highlighted, type=bool, default=False)
