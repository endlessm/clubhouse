#
# Copyright © 2020 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
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

import asyncio
import functools
import glibcoro
import os
import pkgutil
import shutil
import subprocess
import sys

from collections import OrderedDict
from datetime import date, datetime
from enum import Enum, IntEnum
from eosclubhouse import config, logger
from eosclubhouse.achievements import AchievementsDB
from eosclubhouse.network import NetworkManager
from eosclubhouse.system import App, Desktop, GameStateService, Sound, ToolBoxCodeView, \
    UserAccount, Tour
from eosclubhouse.utils import (get_alternative_quests_dir, get_flatpak_sandbox,
                                ClubhouseState, MessageTemplate, Performance,
                                QuestStringCatalog, convert_variant_arg, Version)
from eosclubhouse import metrics
from gi.repository import Gdk, Gio, Gtk, GObject, GLib


# Parse Clubhouse version ignoring micro
clubhouse_version = Version(config.PROJECT_VERSION, ignore_micro=True)

# Set up the asyncio loop implementation
glibcoro.install()


class Registry(GObject.GObject):

    _quest_sets_to_register = []
    _quest_sets = []
    _quest_instances = {}
    _loaded_modules = set()
    _loaded_episode = None
    _autorun_quest = None
    _singleton = None

    __gsignals__ = {
        'schedule-quest': (
            GObject.SignalFlags.RUN_FIRST, None, (str, bool, int)
        ),
    }

    def __init__(self):
        super().__init__()

    @classmethod
    def get_or_create(class_):
        if class_._singleton is None:
            class_._singleton = class_()
        return class_._singleton

    def schedule_quest(self, quest_name, confirm_before=True, start_after=3):
        self.emit('schedule-quest', quest_name, confirm_before, start_after)

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
            quest_set = quest_set_class()
            class_._quest_sets.append(quest_set)
            logger.debug('QuestSet registered: %s', quest_set_class)

        # @todo: Prevent iterating twice.
        for quest_set_class in class_._quest_sets_to_register:
            quest_set = quest_set_class()
            for quest in quest_set.get_quests():
                quest.sync_from_conf()

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
    def get_questset_for_character(class_, character_id):
        for qs in class_.get_quest_sets():
            if qs.get_character() == character_id:
                return qs
        return None

    @classmethod
    def get_questset_for_quest(class_, quest):
        # Note: this assumes that the questsets don't share quests. If
        # not, it will return the first questset matching.
        for qs in class_.get_quest_sets():
            if quest in qs.get_quests():
                return qs
        return None

    @classmethod
    def get_quest_set_by_name(class_, name):
        for quest_set in class_.get_quest_sets():
            if quest_set.get_id() == name:
                return quest_set

        return None

    @classmethod
    def has_quest_sets_highlighted(class_):
        return any(qs.highlighted for qs in class_.get_quest_sets())

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

            # loading custom quests on HOME folder. This should be done before
            # the episode loading because in other case the quest is not added
            # to the pathway
            class_.load(get_alternative_quests_dir())

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
        if class_._autorun_quest is not None:
            quest = class_.get_quest_by_name(class_._autorun_quest)
            if quest is not None and not quest.complete:
                return class_._autorun_quest

        return None

    @classmethod
    def get_next_auto_offer_quest(class_, current_quest=None):
        for quest_set in class_.get_quest_sets():
            for quest in quest_set.get_quests():
                if quest == current_quest:
                    continue
                if quest.auto_offer and quest.available and not quest.conf['complete']:
                    return quest

        return None

    @classmethod
    def try_offer_quest(class_, current_quest=None):
        next_quest = class_.get_next_auto_offer_quest(current_quest)
        if next_quest:
            logger.debug('Proposing next quest: %s', next_quest)
            registry = class_.get_or_create()
            registry.schedule_quest(next_quest.get_id(), **next_quest.get_auto_offer_info())

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

            # custom quest in the HOME folder doesn't have a real episode name
            # and the module is quests
            is_alternative_quests = 'quests' == episode
            if not is_alternative_quests and episode != current_episode:
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

            result = None

            try:
                # Execute the step
                logger.debug('Executing step: %s%r', step_func.__name__, args_)
                result = step_func(*args_)

            except asyncio.CancelledError:
                logger.debug('Async action cancelled.')

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

        loop = async_action.future.get_loop()
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

        self._current_waiting_loop = loop = asyncio.new_event_loop()

        loop.run_until_complete(wait_or_timeout(futures, timeout))
        loop.stop()
        loop.close()

        self._current_waiting_loop = None

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
    DEFAULT_ACHIEVEMENT_POINTS = 1
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
    }

    _SOUND_ON_RUN_BEGIN = 'quests/quest-given'
    _OPEN_DIALOG_SOUND = 'clubhouse/dialog/open'
    _ABORT_SOUND = 'quests/quest-aborted'
    _PROPOSAL_SOUND = 'quests/quest-proposed'

    # @todo: Document
    __available_after_completing_quests__ = []

    _DEFAULT_TIMEOUT = 2 * 3600  # secs

    _DEFAULT_CHARACTER = 'ada'
    _DEFAULT_MOOD = 'talk'

    since = None

    stop_timeout = GObject.Property(type=int, default=_DEFAULT_TIMEOUT)

    stopping = GObject.Property(type=bool, default=False)

    @property
    def proposal_sound(self):
        return self._PROPOSAL_SOUND

    def __init__(self):
        super().__init__()

        self._labels = {
            'QUEST_ACCEPT': 'Sure!',
            'QUEST_REJECT': 'Not now…',
            'QUEST_ACCEPT_STOP': 'Yes',
            'QUEST_REJECT_STOP': 'No',
            'QUEST_ACCEPT_HARDER': 'Yes',
            'QUEST_REJECT_HARDER': 'No',
            'QUEST_NAME': '',
            'QUEST_SUBTITLE': 'Summary',
            'QUEST_DESCRIPTION': None,
            'QUEST_CONTENT_TAGS': None,
            'QUEST_CONTENT_TAGS_TITLE': 'Objectives',
        }

        self._load_since()

        # We declare these variables here, instead of looking them up in the registry when
        # we need them because this way we ensure we get the values when the quest was loaded,
        # and eventually prevent situations where the quest uses these values from the Registry
        # but meanwhile a new episode has been loaded (unlikely, but disastrous if it happens).
        self._episode_name = Registry.get_loaded_episode_name()

        self._qs_base_id = self.get_default_qs_base_id()

        self._last_bg_sound_uuid = None
        self._last_bg_sound_event_id = None

        self._characters = {}

        self._setup_labels()

        self.gss = GameStateService()
        self.conf = {}
        self.load_conf()

        self._highlighted = False
        self._available = self._get_availability()
        if self.get_dependency_quests() != []:
            self.gss.connect('changed', lambda _gss: self._update_availability())
            self._update_availability()

        self._cancellable = None

        self._confirmed_step = False

        self._toolbox_topic_clicked = None

        self._run_context = None

        self._app = None

        self.reset_hints_given_once()

        self.clubhouse_state = ClubhouseState()

        self._is_new = False
        self._update_is_new()

        self.setup()

        # update availability again here because available_since and
        # available_until are usually updated in the setup method and the
        # 'notify::available-since' signal could cause race conditions
        self._available = self._get_availability()

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

        # @todo: Remove this when updating to a runtime using Pango >= 1.44, because
        # insert_hyphens is not supported in the current version of our runtime.
        if self.is_narrative():
            parsed_text = message_info['parsed_text']
            message_info['parsed_text'] = parsed_text.replace('insert_hyphens="true"', '')
            message_info['parsed_text'] = parsed_text.replace('insert_hyphens="false"', '')

        return message_info

    def _setup_labels(self):
        for message_id in self._labels:
            label = QuestStringCatalog().get_string(f'{self._qs_base_id}_{message_id}')
            if label:
                self._labels[message_id] = label

    def get_label(self, message_id):
        return self._labels[message_id]

    def get_episode_name(self):
        return self._episode_name

    def get_dependency_quests(self):
        return self.__available_after_completing_quests__

    def _is_contemporary_available(self):
        if self.available_since or self.available_until:
            # Remove minutes and seconds from time
            today = datetime(*datetime.now().timetuple()[:3])
            start = today
            end = today

            if self.available_since:
                start = datetime.strptime(self.available_since, '%Y-%m-%d')
            if self.available_until:
                end = datetime.strptime(self.available_until, '%Y-%m-%d')

            return start <= today <= end

        return True

    def _get_availability(self):
        # First we check if the quest should be available at this datetime:
        if not self._is_contemporary_available():
            return False

        # Then we check if this quest depends on others, and if so if they are
        # complete:
        return all(self.is_named_quest_complete(q)
                   for q in self.get_dependency_quests())

    def _update_availability(self):
        self.available = self._get_availability()

    def get_default_qs_base_id(self):
        return str(self.__class__.__name__).upper()

    def _start_record_metrics(self):
        pathways = [i.get_name() for i in self.get_pathways()]
        key = self.get_name()
        payload = (self.complete, self.get_id(), pathways)
        metrics.record_start('QUEST', key, payload)

    def _stop_record_metrics(self):
        pathways = [i.get_name() for i in self.get_pathways()]
        key = self.get_name()
        payload = (self.complete, self.get_id(), pathways)
        metrics.record_stop('QUEST', key, payload)

        # recording quest completeness and a single event because right now
        # azafea doesn't store the progress stop event
        payload = {
            "complete": self.complete,
            "quest": self.get_id(),
            "pathways": pathways,
            "progress": Registry.get_current_episode_progress() * 100,
        }
        metrics.record('PROGRESS_UPDATE', payload)

    def run(self, on_quest_finished):
        assert hasattr(self, 'step_begin'), ('Quests need to declare a "step_begin" method, in '
                                             'order to be run.')

        self.run_in_context(on_quest_finished)

    def run_in_context(self, quest_finished_cb):
        Sound.play(self._SOUND_ON_RUN_BEGIN)

        # Reset the "stopping" property before running the quest.
        self.stopping = False

        # Reset the hints given once:
        self.reset_hints_given_once()

        self._run_context = _QuestRunContext(self._cancellable)

        # Save last launch date
        self.conf['last_launch_date'] = date.today().isoformat()
        self._update_is_new()

        self.emit('quest-started')
        self._start_record_metrics()

        if self.requires_network() and not self.has_connection():
            self._run_context.run(self.step_no_connection)
        elif self.app is not None and not self.app.is_installed():
            self._run_context.run(self.step_app_not_installed)
        else:
            self._run_context.run(self.step_begin)

        self._run_context = None

        self.run_finished()
        quest_finished_cb(self)

        self.emit('quest-finished')
        self._stop_record_metrics()

        # The quest is stopped, so reset the "stopping" property again.
        self.stopping = False

    def run_finished(self):
        """This method is called when a quest finishes running.

        It can be overridden when quests need to run logic associated with that moment. By default
        it schedules the next quest to be run (if there's any).
        """
        Registry.try_offer_quest(self)

    def set_next_step(self, step_func, delay=0, args=()):
        assert self._run_context is not None
        self._run_context.set_next_step(step_func, delay, args)

    def wait_for_app_js_props_changed(self, app=None, props=None, timeout=None):
        return self.connect_app_js_props_changes(app, props).wait(timeout)

    def connect_app_object_props_changes(self, app, obj, props):
        assert len(props) > 0
        return self._connect_app_changes(app, obj, props)

    def connect_app_js_props_changes(self, app=None, props=None):
        if app is None:
            app = self.app
        if props is None:
            props = []
        return self.connect_app_object_props_changes(app, app.APP_JS_PARAMS, props)

    def connect_app_quit(self, app=None):
        if app is None:
            app = self.app
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

    # @todo: Is this still needed?
    def get_confirm_action(self):
        assert self._run_context is not None

        async_action = self._run_context.get_confirm_action()
        return async_action

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
        # See Quest.step_abort()
        raise DeprecationWarning

    def stop(self):
        if not self.is_cancelled() and self._cancellable is not None:
            self.play_stop_bg_sound(sound_event_id=None)
            self._cancellable.cancel()

    def get_main_character(self):
        questset = Registry.get_questset_for_quest(self)
        if questset is None:
            return self._DEFAULT_CHARACTER

        return questset.get_character()

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
        return {'user_name': UserAccount().get('RealName')}

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

    @classmethod
    def get_pathways(class_):
        quest_pathways = []
        registered_questsets = Registry.get_quest_sets()
        for tag_info in class_.get_tag_info_by_prefix('pathway'):
            pathway_name = tag_info[0]
            try:
                pathway = \
                    next(p for p in registered_questsets if p.get_name().upper() == pathway_name)
                quest_pathways.append(pathway)
            except StopIteration:
                continue
        return quest_pathways

    def get_name(self):
        return self.get_label('QUEST_NAME')

    @classmethod
    def get_tags(class_):
        return class_.__tags__

    @classmethod
    def get_requires(class_, flag='require'):
        requires = [tag[len(flag) + 1:] for tag in class_.get_tags() if tag.startswith(flag)]
        return requires

    @classmethod
    def requires_network(class_):
        return 'network' in class_.get_requires()

    @classmethod
    def get_auto_offer_info(class_):
        return class_.__auto_offer_info__

    @classmethod
    def get_tag_info_by_prefix(class_, prefix):

        def sanitize(tag_element):
            try:
                return int(tag_element)
            except ValueError:
                return tag_element.upper()

        for tag in class_.get_tags():
            if not tag.startswith(prefix + ':'):
                continue

            yield [sanitize(t) for t in tag.split(':')[1:]]

    @classmethod
    def get_difficulty(class_):
        for tag_info in class_.get_tag_info_by_prefix('difficulty'):
            difficulty = tag_info[0]
            try:
                return getattr(class_.Difficulty, difficulty)
            except AttributeError:
                continue

        return class_.DEFAULT_DIFFICULTY

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

    @classmethod
    def _load_since(class_):
        for tag_info in class_.get_tag_info_by_prefix('since'):
            class_.since = Version(tag_info[0], ignore_micro=True)

    def load_conf(self):
        key = self._get_conf_key()
        self.conf = self.gss.get(key, value_if_missing={})
        self.complete = self.conf.get('complete', False)

    def sync_from_conf(self):
        if self.complete:
            self._give_achievement_points()

    def _give_achievement_points(self, record_points=False):
        manager = AchievementsDB().manager

        def get_points(tag_info):
            if len(tag_info) > 1:
                return tag_info[1]
            return self.DEFAULT_ACHIEVEMENT_POINTS

        # Add points to skillsets in tags:
        for tag_info in self.get_tag_info_by_prefix('skillset'):
            skillset = tag_info[0]
            points = get_points(tag_info)
            manager.add_points(skillset, points, record_points)

        # Don't give automatic points if the quest is hidden in the UI.
        if self.skippable:
            return

        # Add points for pathways:
        for pathway in self.get_pathways():
            pathway_skillset = 'pathway:' + pathway.get_name()
            manager.add_points(pathway_skillset, self.DEFAULT_ACHIEVEMENT_POINTS, record_points)

        # Add points for the difficulty:
        difficulty_skillset = 'difficulty:' + self.get_difficulty().name
        manager.add_points(difficulty_skillset, self.DEFAULT_ACHIEVEMENT_POINTS, record_points)

    def get_complete(self):
        return self.conf['complete']

    def set_complete(self, is_complete):
        if is_complete and self.conf['complete'] != is_complete:
            self._give_achievement_points(record_points=True)
        self.conf['complete'] = is_complete

    def _update_is_new(self):
        is_new = False

        # A new quest is a quest that was introduced in the latest major version
        # of the clubhouse and has not been played by the user.
        # So a quest is new if it has a "since" version and its equal or bigger
        # than the current clubhouse version. (we include bigger versions
        # because of development versions)

        if self.since is not None and self.since >= clubhouse_version:
            is_new = self.conf.get('last_launch_date') is None

        if self._is_new != is_new:
            self._is_new = is_new
            self.notify('is_new')

    def _get_highlighted(self):
        return self._highlighted

    def _set_highlighted(self, is_highlighted):
        if self._highlighted == is_highlighted:
            return
        self._highlighted = is_highlighted
        self.notify('highlighted')

    def get_named_quest_conf(self, class_name, key):
        gss_key = self._get_quest_conf_prefix() + class_name
        data = self.gss.get(gss_key)

        if data is None:
            return None
        return data.get(key)

    def is_named_quest_complete(self, class_name):
        data = self.get_named_quest_conf(class_name, 'complete')
        return data is not None and data

    def with_app_launched(app_name=None, otherwise='step_abort'):
        def wrapper(func):

            def wrapped_func(instance, *args):
                if app_name is None and instance.app is not None:
                    app = instance.app
                else:
                    app = App(app_name)

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

    def with_app_in_foreground(app_name=None, otherwise='step_abort'):
        def wrapper(func):

            def wrapped_func(instance, *args):
                if app_name is None and instance.app is not None:
                    app = instance.app
                else:
                    app = App(app_name)

                app_quit_callback = getattr(instance, otherwise)
                app_was_quit = False
                handler_id = 0

                if not Desktop.is_app_in_foreground(app.dbus_name):
                    return app_quit_callback

                def _app_in_foreground_changed(name, app_name):
                    nonlocal app_was_quit

                    if name != app_name:
                        Desktop.disconnect_app_in_foreground_change(handler_id)
                        app_was_quit = True
                        app_quit_callback()

                handler_id = Desktop.connect_app_in_foreground_change(
                    _app_in_foreground_changed, app.dbus_name)

                ret = func(instance, *args)

                if app_was_quit:
                    return None

                Desktop.disconnect_app_in_foreground_change(handler_id)
                return ret

            return wrapped_func

        return wrapper

    def _get_string_from_catalog(self, message_id):
        '''Get the string, trying an absolute message ID first, then one prefixed.

        Examples:

        .. code-block::

           self._get_string_from_catalog('NOQUEST_ACCEPT')
           self._get_string_from_catalog('MY_QUEST_ACCEPT')  # Being 'MY_QUEST' this quest ID.
           self._get_string_from_catalog('ACCEPT')  # Will try 'MY_QUEST_ACCEPT' first.

        :param str message_id: ID of a message from the strings catalog.

        '''
        return (QuestStringCatalog().get_string(message_id) or
                QuestStringCatalog().get_string(f'{self._qs_base_id}_{message_id}'))

    @classmethod
    def get_pathway_order(class_):
        return class_.__pathway_order__

    @classmethod
    def is_narrative(class_):
        return class_.__is_narrative__

    @classmethod
    def dismissible_messages(class_):
        return class_. __dismissible_messages__

    @classmethod
    def get_id(class_):
        return class_.__name__

    highlighted = GObject.Property(_get_highlighted, _set_highlighted, type=bool, default=False,
                                   flags=GObject.ParamFlags.READWRITE |
                                   GObject.ParamFlags.EXPLICIT_NOTIFY)

    @GObject.Property(type=bool, default=False)
    def is_new(self):
        """Whether this quest is a new release or not"""
        return self._is_new


class Quest(_Quest):
    '''Hack Quests are written by subclassing this class.

    - Define your quest using attributes like :attr:`__tags__` below.
    - Write a :meth:`step_begin()` method.
    - Build the flow of steps by returning the name of the next step from steps.
    - Finish by returning :meth:`step_complete_and_stop()` from a step.
    '''

    # ** Properties **

    __app_id__ = None
    '''ID of the application used by this quest, if any.

    See :attr:`app`.

    '''

    __app_common_install_name__ = None
    '''If this quest's app is used by several quests, it may have a common install string
    in the 'NOQUEST' section of the string database. See step_app_not_installed()
    '''

    __app_repository__ = config.DEFAULT_INSTALL_REPO
    '''Repository of the application used by this quest, otherwise the default repo.'''

    __tags__ = []
    '''Generic tags for the quest.

    This is a list of generic tags (strings). There are tags treated specially, they start with
    a prefix separated of the rest by a colon:

    - 'pathway:SOME_PATHWAY' -- Makes this quest belong to a pathway.

    - 'difficulty:SOME_DIFFICULTY' -- Define the difficulty of this quest. Can be 'easy',
      'normal' or 'hard'.

    - 'require:network' -- Define if the quest requires a internet connection to be played.

    '''

    __pathway_order__ = 0
    '''Order of this quest in pathways.

    Quests in the same pathway will be sorted by this number. A smaller number will make the
    quest appear closer to the beginning of the list.

    '''

    __is_narrative__ = False
    '''Whether the quest is narrative or not.'''

    __dismissible_messages__ = True
    '''Whether the quest is dismissible or not.'''

    __auto_offer_info__ = {'confirm_before': True, 'start_after': 3}
    '''A dictionary containing the information for auto-offered quests.

    If the quest is automatically offered, this information is used to:

    - Key 'confirm_before' -- Defines if the auto-offer needs to be confirmed by the user. If
      so, a popup message will ask the user for confirmation.

    - Key 'start_after' -- Defines the amount of seconds to wait before automatically offering
      the quest.

    '''

    __items_on_completion__ = {}
    '''Items expected to be set once the quest is complete.

    Should be in the form 'key': {...} , a dict of the key's content, or an empty dict for
    using the default key's content.

    '''

    __conf_on_completion__ = {}
    '''Quest configuration expected to be set once the quest is complete.

    Should be in the form 'key': {...} , a dict of the key's content, or an empty dict for
    using the default key's content.

    '''

    # @todo: This should be __auto_offer__ like other Quest attributes.
    auto_offer = GObject.Property(type=bool, default=False)
    '''Defines if this quest is automatically offered as soon as it is available.

    Define this in the :meth:`setup()` method.
    '''

    available_since = GObject.Property(type=str, default='')
    '''Defines the quest availability start date in the following form YYYY-MM-DD.'''

    available_until = GObject.Property(type=str, default='')
    '''Defines the quest availability end date in the following form YYYY-MM-DD.'''

    # @todo: This should be __skippable__ like other Quest attributes.
    skippable = GObject.Property(type=bool, default=False)
    '''True if the quest shouldn't be presented in the UI.

    Define this in the :meth:`setup()` method.
    '''

    def _get_available(self):
        return self._available

    def _set_available(self, value):
        if self._available == value:
            return
        self._available = value
        self.notify('available')

    available = GObject.Property(_get_available, _set_available, type=bool, default=True,
                                 flags=GObject.ParamFlags.READWRITE |
                                 GObject.ParamFlags.EXPLICIT_NOTIFY)
    '''Property that holds if the quest is available or not.

    Set `self.available = False` when you want this the quest to not be avaiable anymore. Or
    use the :meth:`step_complete_and_stop()` method, which does it for you.

    '''

    def _get_complete(self):
        return self.get_complete()

    def _set_complete(self, is_complete):
        self.set_complete(is_complete)
        self.notify('complete')

    complete = GObject.Property(_get_complete, _set_complete, type=bool, default=False,
                                flags=GObject.ParamFlags.READWRITE |
                                GObject.ParamFlags.EXPLICIT_NOTIFY)
    '''Property that holds if the quest is complete or not.

    Set `self.complete = True` when the quest is completed. Or use the
    :meth:`step_complete_and_stop()` method, which does it for you.

    '''

    @property
    def app(self):
        '''Instance of the application object as defined by :attr:`__app_id__`.

        If `__app_id__` is set, this will be an instance with methods to manage the
        application. Otherwise this will be None.

        '''
        if self.__app_id__ is None:
            return None
        if self._app is None:
            # @todo: For now we instantiate the generic App class. In
            # the future we might want to instantiate subclasses of
            # App living in the eosclubhouse.apps module, like
            # Sidetrack, depending on the app ID specified.
            self._app = App(self.__app_id__)
        return self._app

    def __init__(self):
        super().__init__()
        self.connect('notify::available-since', lambda _a, _b: self._update_availability())
        self.connect('notify::available-until', lambda _a, _b: self._update_availability())

    # ** Setup and steps **

    def setup(self):
        '''Initialize/setup anything that is related to the quest implementation.

        Instead of having to define a constructor, subclasses of Quest should set up anything
        related to their construction in this method. This way Quest implementations should
        only define a constructor when needed, which simplifies the quests making them more
        readable.

        This method is called just once (in the Quest's base constructor). Code that needs to
        be called on every quest run, should be added to the :meth:`step_begin()` method.

        Example:

        .. code-block::

           def setup(self):
               self.auto_offer = True
               self.skippable = True

        '''
        pass

    def step_begin(self):
        '''Step method that is executed when the quest runs.

        This method must be defined by subclasses of Quest.

        Steps must return the name of the next step to be executed. This is how you can build
        the control flow. The last step must complete and stop the quest. You can ues the
        :meth:`step_complete_and_stop()` method, or write your own.

        Example:

        .. code-block::

           def step_begin(self):
               # ...
               return self.step_play

           def step_play(self):
               # ...
               return self.step_complete_and_stop

        :returns: The name of the next step. Example: `return self.step_play`.

        '''
        raise NotImplementedError

    def step_no_connection(self):
        '''Step method that is executed when there's no internet connection.

        This method is launched instead of step_begin when there is no
        interent connection and the quest has the tag 'require:network'

        By default shows a message and then abort.
        '''

        self.wait_confirm('NOQUEST_NOCONNECTION')
        return self.step_abort

    def step_app_not_installed(self):
        '''Step method that is executed to check if the corresponding app is installed.

        This method is launched before the actual quest is run. It will
        guide the user through the installation of the app through the
        software backend.

        If __app_common_install_name__ is defined, it will be used to construct the install
        question's string.
        Failing that, if there is a quest-specific _NOTINSTALLED string available, it is used.
        Finally, it falls back on the generic NOTINSTALLED string.
        '''

        if self.__app_common_install_name__ is not None:
            install_msg = 'NOQUEST_' + self.__app_common_install_name__ + '_NOTINSTALLED'
        else:
            has_install_msg = self._get_message_info('{}_NOTINSTALLED'.format(self._qs_base_id))
            install_msg = 'NOTINSTALLED' if has_install_msg else 'NOQUEST_NOTINSTALLED_GENERIC'

        action = self.show_choices_message(install_msg,
                                           ('NOQUEST_POSITIVE', None, True),
                                           ('NOQUEST_NEGATIVE', None, False)).wait()
        if action.future.result():
            self.show_message('NOQUEST_AUTOINSTALL')
            self.wait_for_app_install(self.app, confirm=False, repo=self.__app_repository__)
            return self.step_begin
        else:
            return self.step_abort

    def step_complete_and_stop(self, available=True):
        '''Step method that completes and stop the quest.

        :param bool available: Whether to keep the quest avaiable or not.

        '''
        self.complete = True
        self.available = available
        Sound.play('quests/quest-complete')
        self.stop()

    def step_abort(self):
        '''Step method to abort the quest.

        The quest will display the ABORT message, if it exists for this quest in the strings
        catalog. Otherwise it will play a default abort NOQUEST_DEFAULT_ABORT message. And
        finally, the quest will be stopped.

        '''
        if self.stopping:
            return

        # Notify we're going to stop soon
        self.stopping = True

        abort_info = self._get_message_info('{}_ABORT'.format(self._qs_base_id))
        if abort_info:
            self.show_message('ABORT')
        # Narrative quests doesn't show the default abort message
        elif not self.is_narrative():
            self.show_message('NOQUEST_DEFAULT_ABORT')

        if not self.is_narrative():
            self.pause(5)

        self.stop()

    # ** Obtaining and displaying messages **

    def get_loop_messages(self, prefix, start=1):
        '''Return a circle list with all message IDs that have the given prefix, in order.

        Example: Consider that 'MYQUEST_INFO_1' and 'MYQUEST_INFO_2' exist in the catalog:

        >>> info_messages = self.get_loop_messages(prefix='INFO')
        >>> info_messages[0]
        'MYQUEST_INFO_1'
        >>> info_messages[1]
        'MYQUEST_INFO_2'

        Since it's a circle list, the index can go out of bounds:

        >>> info_messages[5]
        'MYQUEST_INFO_1'

        >>> info_messages[-5]
        'MYQUEST_INFO_2'

        :param str prefix: ID of a message from the strings catalog.
        :param int start: Start at a different number. By default it's 1.

        '''
        if not prefix.startswith(self._qs_base_id):
            prefix = f'{self._qs_base_id}_{prefix}'
        return QuestStringCatalog.get_loop_messages(prefix, start)

    def show_message(self, message_id=None, **options):
        '''Show a dialogue displayig the message with ID `message_id`.

        The `message_id` must exist in the catalog. It's prefix can be omitted, in which case
        the quest's name will be used as prefix.

        :param str message_id: ID of a message from the strings catalog.
        :param dict **options: The keyword arguments are documented below:

        :param bool narrative: True if the message is narrative. By default this displays a
            popup message in the Desktop, outside the Clubhouse. Passing `narrative=True` will
            display a narrative message inside the Clubhouse, instead of a popup message. Note:
            only narrative quests can display narrative messages. See :attr:`__is_narrative__`.

        :param list choices: List of choices to display as buttons. Each choice is defined with
            a tuple(text, callback, *args). Also see :meth:`show_choices_message()` to do it
            automatically.

        :param bool use_confirm: True to add a confirmation button. See
            :meth:`show_confirm_message()` to do it automatically.

        :param str confirm_label: Change the label of the confirm button. By default it's '❯'.

        '''
        if message_id is not None:
            full_message_id = self._qs_base_id + '_' + message_id
            info = self._get_message_info(full_message_id)

            # Fallback to the given message_id if no string was found
            if info is None:
                info = self._get_message_info(message_id)
            else:
                message_id = full_message_id

            if info is None:
                raise NoMessageIdError("Can't show message, the message ID " + message_id +
                                       " is not in the catalog.")

            options.update(info)

        if options.get('narrative', False):
            message_type = self.MessageType.NARRATIVE
        else:
            message_type = self.MessageType.POPUP

        if not self.is_narrative() and message_type == self.MessageType.NARRATIVE:
            logger.warning('Can\'t show message %r, quest %r is not narrative.', message_id, self)
            return

        possible_answers = []
        if options.get('choices'):
            possible_answers = [(text, callback, *args)
                                for text, callback, *args
                                in options['choices']]

        if options.get('use_confirm'):
            confirm_label = options.get('confirm_label', '❯')
            possible_answers = [(confirm_label, self._confirm_step)] + possible_answers

        sfx_sound = options.get('sfx_sound')
        if not sfx_sound:
            if message_id == 'ABORT':
                sfx_sound = self._ABORT_SOUND
            elif message_id == 'QUESTION':
                sfx_sound = self._PROPOSAL_SOUND
            else:
                sfx_sound = self._OPEN_DIALOG_SOUND
        bg_sound = options.get('bg_sound')

        self.emit('message', {
            'id': message_id,
            'text': options['parsed_text'],
            'choices': possible_answers,
            'character_id': options.get('character_id') or self.get_main_character(),
            'character_mood': options.get('mood') or self._DEFAULT_MOOD,
            'sound_fx': sfx_sound,
            'sound_bg': bg_sound,
            'type': message_type,
        })

    def dismiss_message(self, narrative=False):
        '''Dismiss any current message dialogue.

        :param bool narrative: Whether to dismiss a narrative message.

        '''
        self.emit('dismiss-message', narrative)

    def _show_next_hint_message(self, info_list, index=0):
        label = "I'd like another hint"
        if index == 0:
            label = "Give me a hint"
        elif index == len(info_list) - 1:
            label = "What's my goal?"

        message_id = info_list[index]
        next_index = (index + 1) % len(info_list)
        next_hint = functools.partial(self._show_next_hint_message, info_list, next_index)
        self.show_message(message_id=message_id, choices=[(label, next_hint)])

    def show_hints_message(self, message_id, give_once=False):
        '''Show a chain of dialogues displayig hints for the message with ID `message_id`.

        You can use the same message ID with suffixes `_HINT1`, `_HINT2`, etc to display a
        message with a number of hints. The message will loop between initial text and all the
        hints in sequence. For example if you have message IDs in the spreadsheet like:

        - `MYQUEST_FLIP`
        - `MYQUEST_FLIP_HINT1`
        - `MYQUEST_FLIP_HINT2`
        - `MYQUEST_FLIP_HINT3`

        You can display the message with hints in the quest with:

        .. code-block::

           self.show_hints_message('FLIP')

        Passing the parameter `give_once=True` the hints will be given once and then
        ignored. Use :meth:`reset_hints_given_once()` to reset it.

        :param str message_id: ID of a message from the strings catalog.
        :param bool give_once: Whether to give this hint only once.

        '''
        if give_once:
            if message_id in self._hints_given_once:
                return
            else:
                self._hints_given_once.add(message_id)

        full_message_id = self._qs_base_id + '_' + message_id
        message_id_list = QuestStringCatalog.get_hint_keys(full_message_id)

        # Fallback to the given message_id if no string was found
        if message_id_list is None:
            full_message_id = message_id
            message_id_list = QuestStringCatalog.get_hint_keys(full_message_id)

        if len(message_id_list) == 1:
            logger.warning('Asked for messages hints, but no hints were found for ID %s; '
                           'not showing the hints button.', message_id)
            self.show_message(message_id)
        else:
            self._show_next_hint_message(message_id_list)

    def reset_hints_given_once(self):
        '''Reset any hints given once.

        Any hint given with :meth:`show_hints_message()` passing the parameter `give_once=True`
        will be given once and then ignored. This method can be called in a step to reset that
        and give the hint once again.

        '''
        self._hints_given_once = set()

    def wait_for_app_install(self, app=None, confirm=True,
                             repo=config.DEFAULT_INSTALL_REPO, timeout=None):
        '''Wait until `app` is installed.

        :param app: The application. If not passed, it will use :attr:`app`.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :param confirm: If true, the app center will be shown but the
            installation doesn't start automatically. In other case the
            installation will start just after the call.
        :param repo: When confirm = True, you can provide a repository to use
            for the installation. By default it's flathub but it could be
            eos-apps or other flatpak repository.
        :type timeout: int or None
        :rtype: AsyncAction

        '''
        assert self._run_context is not None

        if app is None:
            app = self.app

        async_action = self._run_context.new_async_action()
        if async_action.is_cancelled():
            return async_action

        if app.is_installed():
            async_action.state = AsyncAction.State.DONE
            return async_action

        def _poll_app_install():
            if async_action.is_resolved() or async_action.is_cancelled():
                return GLib.SOURCE_REMOVE

            if app.is_installed():
                async_action.resolve()
                return GLib.SOURCE_REMOVE

            return GLib.SOURCE_CONTINUE

        # Polling the app install state
        GLib.timeout_add_seconds(1, _poll_app_install)

        app.request_install(confirm=confirm, repo=repo)
        self._run_context.wait_for_action(async_action, timeout)
        return async_action

    def show_confirm_message(self, message_id, **options):
        '''Show a message with a "Next" button

        Show a message and automatically add a "Next" button to it.

        :param str message_id: ID of a message from the strings catalog.
        :param **options: See same keyword arguments of :meth:`show_message()`
        :rtype: AsyncAction

        '''
        assert self._run_context is not None

        async_action = self.get_confirm_action()
        if async_action.is_cancelled():
            return async_action

        self._confirmed_step = False
        options.update({'use_confirm': True})
        self.show_message(message_id, **options)

        return async_action

    def wait_confirm(self, message_id=None, timeout=None, **options):
        '''Show confirm message and wait for user confirmation.

        This is the same as calling:

        .. code-block::

           self.show_confirm_message(...).wait()

        :param str message_id: ID of a message from the strings catalog.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :param **options: See same keyword arguments of :meth:`show_message()`

        '''
        return self.show_confirm_message(message_id, **options).wait(timeout)

    def show_choices_message(self, message_id, *user_choices, **options):
        '''Show a message with choices.

        Each choice is composed of a tuple:

        - Option message ID -- The button label is obtained from the catalog with this ID.

        - Callback -- A function to call when the button is pressed. If None, the identity
          function will be used, returning the callback arguments as-is.

        - Callback arguments -- The arguments to pass to the callback function.

        The selected choice will be stored as the result of the returned :class:`AsyncAction`.

        Example:

        .. code-block::

           action = self.show_choices_message('MY_QUESTION',
                                              ('MY_OPTION_A', None, True),
                                              ('MY_OPTION_B', None, False)).wait()

           result = action.future.result()
           if result:
               # ...

        Example with callback:

        .. code-block::

           def _callback(value_a=None, value_b=None):
               return do_something(value_a, value_b)

           action = self.show_choices_message('MY_QUESTION',
                                              ('MY_OPTION_A', _callback, 'ada', 'saniel'),
                                              ('MY_OPTION_B', _callback)).wait()

           value = action.future.result()

        :rtype: AsyncAction

        '''
        assert self._run_context is not None

        async_action = self._run_context.new_async_action()

        if async_action.is_cancelled():
            return async_action

        def _callback_and_resolve(async_action, callback, *callback_args):
            ret = callback(*callback_args)
            async_action.resolve(ret)

        def _identity(*args):
            if len(args) == 1:
                return args[0]
            return args

        choices = options.get('choices', [])
        for option_msg_id, callback, *args in user_choices:
            option_label = self._get_string_from_catalog(option_msg_id)
            if callback is None:
                callback = _identity
            choices.append((option_label, _callback_and_resolve, async_action, callback, *args))

        options.update({'choices': choices})
        self.show_message(message_id, **options)

        return async_action

    # ** App launching **

    def ask_for_app_launch(self, app=None, timeout=None, pause_after_launch=2, message_id='LAUNCH',
                           give_app_icon=True):
        '''Ask the player to launch `app`.

        And wait until the app is launched.

        :param app: The application. If not passed, it will use :attr:`app`.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :param int pause_after_launch: Pause in seconds after the app is launched.
        :param str message_id: The message ID to use in the dialogue. Can be a message with hints.

        '''
        if app is None:
            app = self.app

        if app.is_running() or self.is_cancelled():
            return

        if message_id is not None:
            self.show_hints_message(message_id)

        # wait one second to show the notification, then we can show the app in the destkop
        self.pause(1)

        if give_app_icon:
            self.give_app_icon(app.dbus_name)

        self.wait_for_app_launch(app, timeout=timeout, pause_after_launch=pause_after_launch)

    @classmethod
    def give_app_icon(class_, app_name):
        '''Display the icon for `app_name` in the Desktop.

        You can use `:meth:ask_for_app_launch()` instead to also ask the player to launch the
        app with a dialogue.

        :param app_name: The application name.

        '''
        if not Desktop.is_app_in_grid(app_name):
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(app_name)

        Desktop.focus_app(app_name)

    def wait_for_app_launch(self, app=None, timeout=None, pause_after_launch=0):
        '''Wait until `app` is launched.

        You can use `:meth:ask_for_app_launch()` instead to also ask the player to launch the
        app with a dialogue.

        :param app: The application. If not passed, it will use :attr:`app`.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :param int pause_after_launch: Pause in seconds after the app is launched.
        :rtype: AsyncAction

        '''
        assert self._run_context is not None

        if app is None:
            app = self.app

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

    def wait_for_app_in_foreground(self, app=None, in_foreground=True, timeout=None):
        '''Wait until `app` is in foreground/background.

        :param app: The application. If not passed, it will use :attr:`app`.
        :param in_foreground: Use False to wait for app in background, default is True.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction

        '''
        assert self._run_context is not None
        async_action = self._run_context.new_async_action()

        if app is None:
            app = self.app

        its_done = Desktop.is_app_in_foreground(app.dbus_name)

        if not in_foreground:
            its_done = not its_done

        if its_done:
            async_action.state = AsyncAction.State.DONE
            return async_action

        def _on_app_running_changed(app, async_action):
            if not app.is_running() and not async_action.is_resolved():
                async_action.resolve()

        def _on_app_in_foreground_changed(app_in_foreground_name, app_name, async_action):
            app_name = Desktop.get_app_desktop_name(app_name)

            is_app = app_in_foreground_name == app_name
            if not in_foreground:
                is_app = not is_app

            if is_app and not async_action.is_resolved():
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

    # ** Highlighting **

    def wait_for_highlight_rect(self, x, y, width, height, text='', timeout=None):
        '''Highlight a rectangle on the desktop and wait for user interaction.

        :param x: The x coordinate of the rectangle.
        :param y: The x coordinate of the rectangle.
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        :param text: Optional text to show near the highlighted region.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction
        '''

        return self.wait_for_highlight(x, y, width, height, text,
                                       function='HighlightRect', timeout=timeout)

    def wait_for_highlight_circle(self, x, y, radius, text='', timeout=None):
        '''Highlight a circle on the desktop and wait for user interaction.

        :param x: The x coordinate of the circle.
        :param y: The x coordinate of the circle.
        :param radius: The height of the circle.
        :param text: Optional text to show near the highlighted region.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction
        '''

        return self.wait_for_highlight(x, y, radius, text,
                                       function='HighlightCircle', timeout=timeout)

    def wait_for_highlight_widget(self, name, text='', timeout=None):
        '''Highlight a widget on the desktop and wait for user interaction.

        :param name: The widget name or the style class name.
        :param text: Optional text to show near the highlighted region.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction
        '''

        return self.wait_for_highlight(name, text,
                                       function='HighlightWidget', timeout=timeout)

    def wait_for_highlight_icon(self, app_id, text='', timeout=None):
        '''Highlight a desktop icon and wait for user interaction.

        :param app_id: The app id.
        :param text: Optional text to show near the highlighted region.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction
        '''

        return self.wait_for_highlight(app_id, text,
                                       function='HighlightDesktopIcon', timeout=timeout)

    def wait_for_highlight_fuzzy(self, position='center', size='20%',
                                 shape='rect', text='', timeout=None):
        '''Highlight a region with a fuzzy description and wait for user interaction.

        :param position: The highlight position.
        :param size: The highlight size.
        :param shape: The highlight shape, rect or circle.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction

        These are the supported rules:

          position: "y-axis x-axis|y-axis|x-axis"
          size: "width height|width AR|width"
          shape: "rect|circle"

        where:

          y-axis: "top|center|bottom|N%|Npx"
          x-axis: "left|center|right|N%|Npx"
          width: "N%|Npx"
          height: "N%|Npx"
          AR: N:N
          N: \\d+
        '''

        return self.wait_for_highlight(position, size, shape, text,
                                       function='HighlightFuzzy', timeout=timeout)

    def wait_for_highlight(self, *args, function='HighlightRect', timeout=None):
        '''Highlight a region on the desktop and wait for user interaction.

        :param function: The TourServer function to use.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction
        '''

        assert self._run_context is not None
        async_action = self._run_context.new_async_action()

        def _on_finished(ret):
            async_action.resolve(not ret)

        Tour._call_method(function, *args, callback=_on_finished)
        self._run_context.wait_for_action(async_action, timeout)

        return async_action

    def show_highlight_rect(self, x, y, width, height, text=''):
        '''Highlight a rectangle on the desktop.

        :param x: The x coordinate of the rectangle.
        :param y: The x coordinate of the rectangle.
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        :param text: Optional text to show near the highlighted region.
        '''

        return self.show_highlight(x, y, width, height, text, function='HighlightRect')

    def show_highlight_circle(self, x, y, radius, text=''):
        '''Highlight a circle on the desktop.

        :param x: The x coordinate of the circle.
        :param y: The x coordinate of the circle.
        :param radius: The height of the circle.
        :param text: Optional text to show near the highlighted region.
        '''

        return self.show_highlight(x, y, radius, text, function='HighlightCircle')

    def show_highlight_widget(self, name, text=''):
        '''Highlight a widget on the desktop.

        :param name: The widget name or the style class name.
        :param text: Optional text to show near the highlighted region.
        '''

        return self.show_highlight(name, text, function='HighlightWidget')

    def show_highlight_icon(self, app_id, text=''):
        '''Highlight a desktop icon.

        :param app_id: The app id.
        :param text: Optional text to show near the highlighted region.
        '''

        return self.show_highlight(app_id, text, function='HighlightDesktopIcon')

    def show_highlight_fuzzy(self, position='center', size='20%', shape='rect', text=''):
        '''Highlight a region with a fuzzy description.

        :param str size: The highlight size description. The format is the
            same as the size parameter of the :meth:wait_for_highlight_fuzzy()
            method.
        :param str position: The highlight position description. The format is the
            same as the position parameter of the :meth:wait_for_highlight_fuzzy()
            method.
        :param shape: The highlight shape, rect or circle.
        '''

        return self.show_highlight(position, size, shape, text, function='HighlightFuzzy')

    def show_highlight(self, *args, function='HighlightRect'):
        '''Highlight a region on the desktop.

        :param function: The TourServer function to use.
        '''

        Tour._call_method(function, *args)

    # ** Network detection **

    def has_connection(self):
        return NetworkManager.is_connected()

    # ** Control flow **

    def pause(self, secs):
        '''Pause the execution for `secs` seconds.

        :param int secs: Amount of seconds to pause.
        :rtype: AsyncAction

        '''
        assert self._run_context is not None
        return self._run_context.pause(secs)

    def wait_for_one(self, action_list, timeout=None):
        '''Wait until one of the actions is resolved.

        After this returns, You should check which of the actions has resolved.

        :param list action_list: List of :class:`AsyncAction`.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None

        '''
        self._run_context.wait_for_one(action_list, timeout)

    # ** Configuration **

    def get_conf(self, key):
        '''Get the configuration stored for the quest.

        This is loaded automatically when the quest is instantiated.

        '''
        return self.conf.get(key)

    def set_conf(self, key, value):
        '''Set configuration to be stored for the quest.

        You should call :meth:`save_conf()` to store the changes.

        '''
        self.conf[key] = value

    def save_conf(self):
        '''Store the configuration of the quest.

        This is stored in the game-state-service, in a special section for this quest.

        '''
        conf_key = self._get_conf_key()
        variant = convert_variant_arg(self.conf)
        self.gss.set_async(conf_key, variant)

        if self.complete:
            for item_id, extra_info in self.__items_on_completion__.items():
                self._set_item(item_id, extra_info, skip_if_exists=True)

            for item_id, info in self.__conf_on_completion__.items():
                self.gss.set(item_id, info)

    # ** Highlighting elements of the UI **

    def highlight_character(self, character_id=None):
        '''Highlight a character in the Clubhouse main view.

        :param character_id: The character ID to be highlighted. None to highlight the main
            character of this quest.
        :type character_id: str or None

        '''
        if character_id is not None:
            questset = Registry.get_questset_for_character(character_id)
            if questset is None:
                logger.warning('Quest "%s" is trying to highlight character "%s", but there is'
                               ' no questset matching.', self, character_id)
                return

        else:
            questset = Registry.get_questset_for_quest(self)
            if questset is None:
                logger.warning('Quest "%s" is trying to highlight a character, but it doesn\'t'
                               ' belong to any questset.', self)
                return
            questset = self._questset

        questset.highlighted = True

    def highlight_quest(self, quest_name):
        '''Highlight a quest listed in the UI.

        :param str quest_name: The quest to be highlighted.

        '''
        other_quest = Registry.get_quest_by_name(quest_name)
        if other_quest:
            other_quest.props.highlighted = True

    def highlight_profile_button(self):
        '''Highlight the Profile button.
        '''
        state = ClubhouseState()
        state.user_button_highlighted = True

    def highlight_hack_switch(self):
        '''Highlight the Hack switch.
        '''
        state = ClubhouseState()
        state.hack_switch_highlighted = True

    def highlight_nav(self, nav_name):
        '''Highlight a nav button.

        :param str nav_name: The nav to be highlighted. One of CLUBHOUSE, PATHWAYS, NEWS

        '''

        state = ClubhouseState()
        new_nav = None
        if nav_name:
            new_nav = ClubhouseState.Page[nav_name]

        state.nav_attract_state = new_nav

    # ** Toolbox **

    def wait_for_codeview_errors(self, topic, app=None, errors=False, timeout=None):
        '''Wait until the toolbox `codeview` number of errors is equal to `errors`.

        :param topic: The topic name of the codeview, for example 'instructions'.
        :param app: The application. If not passed, it will use :attr:`app`.
        :param errors: True to wait for errors, False to wait for no errors.
        :param timeout: If not None, the wait will timeout after this amount of seconds.
        :type timeout: int or None
        :rtype: AsyncAction

        '''
        assert self._run_context is not None

        if app is None:
            app = self.app

        async_action = self._run_context.new_async_action()
        if async_action.is_cancelled():
            return async_action

        toolbox = ToolBoxCodeView(app.dbus_name, topic)
        if toolbox.errors == errors:
            async_action.state = AsyncAction.State.DONE
            return async_action

        def _on_errors_change(toolbox, _pspec):
            if toolbox.errors == errors and not async_action.is_resolved():
                async_action.resolve()

        handler_id = toolbox.connect('notify::errors', _on_errors_change)
        self._run_context.wait_for_action(async_action, timeout)
        toolbox.disconnect(handler_id)

        return async_action

    # ** MISC **

    def deploy_file(self, file_path, directory_path, override=False):
        '''Deploy a file inside the player home directory.

        The files should be commited in GIT in the folder specified below:

        :param str file_name: Name of a file that should be already commited in GIT, inside the
            'data/quests_files/' folder.

        :param str directory_path: Destination of the file. It can be either A. the name of a
            "well-known" user folder like DOCUMENTS (see `man xdg-user-dir` for the full list)
            or B: Path to a destination directory inside the user home directory. In this
            latter case it should start with '~/'. The directory (and subdirectories) will be
            created.

        :param bool override: Pass True to override the file if it already exists.

        '''

        if directory_path.startswith('~/'):
            dest_dir = os.path.expanduser(directory_path)
        else:
            dest_dir = subprocess.check_output(['/usr/bin/xdg-user-dir', directory_path],
                                               universal_newlines=True).strip()

            # xdg-user-dir outputs the path to the home dir when there is no match.
            if dest_dir == os.path.expanduser('~'):
                logger.error("Error copying file, directory_path %s is not a well-known user"
                             " directory and  doesn't start with '~/'",
                             directory_path)
                return

        source = os.path.join(config.QUESTS_FILES_DIR, file_path)
        file_name = os.path.basename(file_path)
        destination = os.path.join(dest_dir, file_name)

        if not os.path.exists(source):
            logger.error('Error copying file, source doesn\'t exist: %s', source)
            return

        if not override and os.path.exists(destination):
            logger.error('Error copying file, destination already exists: %s', destination)
            return

        os.makedirs(dest_dir, exist_ok=True)
        shutil.copyfile(source, destination)

    def onboarding_image(self, file_path, size='50% 16:9'):
        '''Show a image with the onboarding extension.

        The files should be commited in GIT in the folder specified below:

        :param str file_path: Name of a file that should be already commited in GIT, inside the
            'data/quests_files/' folder.

        :param str size: The final image size description. The format is the
            same as the size parameter of the :meth:wait_for_highlight_fuzzy()
            method.
        '''

        # convert flatpak path to host absolute path
        quest_files_dir = config.QUESTS_FILES_DIR.replace('/app/', '')
        source = os.path.join(get_flatpak_sandbox(), quest_files_dir, file_path)
        Tour.show_image(source, size)

    def onboarding_clean(self):
        ''' Removes all onboarding extension highlights and images '''

        Tour.clean()

    def onboarding_overview(self, show=True):
        ''' Show or hide the overview on the desktop

        :param bool show: if True the overview will be shown, otherwise it'll
            be hidden.
        '''

        Tour.show_overview(show)

    def open_url_in_browser(self, url):
        """Open the given URL in an external browser.

        :param str url: The URL to open.
        """
        return Gio.AppInfo.launch_default_for_uri_async(url)

    def open_pdf(self, filename):
        """Open the given file in an external app.

        :param str filename: The pdf filename to open.

        The file should exists in the quests_files/pdf folder.
        """

        path = os.path.join(config.QUESTS_FILES_DIR, 'pdf', filename)
        gio_path = f'file://{path}.pdf'
        app = Gio.Application.get_default()

        if app:
            win = app.get_active_window()
            if win:
                return Gtk.show_uri_on_window(win, gio_path, Gdk.CURRENT_TIME)

        # If there's no window we launch directly without attaching to any
        # window
        return Gio.AppInfo.launch_default_for_uri_async(gio_path)


class QuestSet(GObject.GObject):

    __quests__ = []
    __pathway_name__ = None
    __character_id__ = None
    __empty_message__ = 'Nothing to see here!'

    visible = GObject.Property(type=bool, default=True)

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

        self._highlighted = False

        for quest in self.get_quests():
            quest.connect('notify',
                          lambda quest, param: self.on_quest_properties_changed(quest, param.name))

    @classmethod
    def get_tag(class_):
        return 'pathway:' + class_.__pathway_name__.lower()

    def _sort_quests(self):
        def by_order(quest):
            return quest.get_pathway_order()

        self._quest_objs.sort(key=by_order)

    @classmethod
    def get_id(class_):
        return class_.__name__

    def get_quests(self):
        return self._quest_objs

    def __repr__(self):
        return self.get_id()

    @classmethod
    def get_name(class_):
        return class_.__pathway_name__

    @classmethod
    def get_icon_name(class_):
        name = class_.__pathway_name__.lower().replace(" ", "")
        return 'clubhouse-pathway-' + name + '-symbolic'

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
        logger.debug('Quest "%s" property changed: %s to %r', quest, prop_name,
                     quest.get_property(prop_name))
        if prop_name == 'available':
            Registry.try_offer_quest()

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

    highlighted = GObject.Property(_get_highlighted, _set_highlighted, type=bool, default=False)
