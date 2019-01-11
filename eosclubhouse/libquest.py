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

import functools
import os
import pkgutil
import sys
import time

from eosclubhouse import config
from eosclubhouse import logger
from eosclubhouse.system import GameStateService, Sound
from eosclubhouse.utils import get_alternative_quests_dir, Performance, QuestStringCatalog
from gi.repository import GObject, GLib


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
    def get_current_episode(class_):
        current_episode_name = config.DEFAULT_EPISODE_NAME
        current_episode_completed = False
        current_episode = GameStateService().get('clubhouse.CurrentEpisode')
        if current_episode is not None:
            current_episode_name = current_episode.get('name', config.DEFAULT_EPISODE_NAME)
            current_episode_completed = current_episode.get('completed', False)
        return {'name': current_episode_name, 'completed': current_episode_completed}


class Quest(GObject.GObject):

    __gsignals__ = {
        'message': (
            GObject.SignalFlags.RUN_FIRST, None, (str, GObject.TYPE_PYOBJECT, str, str, str)
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

    def __init__(self, name, main_character_id, initial_msg):
        super().__init__()
        self._name = name

        self._qs_base_id = self.get_default_qs_base_id()
        self._initial_msg = initial_msg

        self._characters = {}

        self._main_character_id = main_character_id
        self._main_mood = 'talk'
        self._main_open_dialog_sound = 'clubhouse/dialog/open'

        self._available = True
        self._cancellable = None

        self.gss = GameStateService()

        self.conf = {}
        self.load_conf()

        self.key_event = False
        self._debug_skip = False

        self._confirmed_step = False

        self._timeout_start = -1
        self._check_timeout = False

    def get_default_qs_base_id(self):
        return str(self.__class__.__name__).upper()

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

    def _check_timed_out(self, current_time_secs):
        if not self._check_timeout:
            return

        timeout_start = self._timeout_start
        if timeout_start == -1:
            self._timeout_start = current_time_secs
            return

        if self.stop_timeout != -1 and (current_time_secs - timeout_start) > self.stop_timeout:
            self.stop()

    def _reset_timeout(self):
        self._check_timeout = False
        self._timeout_start = -1

    def set_to_background(self):
        self._check_timeout = True

    def set_to_foreground(self):
        self._reset_timeout()

    def step_first(self, time_in_step):
        raise NotImplementedError

    def get_continue_info(self):
        return (self.continue_message, 'Continue', 'Stop')

    def _confirm_step(self):
        Sound.play('clubhouse/dialog/next')
        self._confirmed_step = True

    def confirmed_step(self):
        confirmed = self._confirmed_step
        self._confirmed_step = False
        return confirmed

    def stop(self):
        if not self.is_cancelled() and self._cancellable is not None:
            self._cancellable.cancel()

    def get_main_character(self):
        return self._main_character_id

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
            possible_answers = [('>', self._confirm_step)] + possible_answers

        self._emit_signal('message', options['txt'], possible_answers,
                          options.get('character_id') or self._main_character_id,
                          options.get('mood') or self._main_mood,
                          options.get('open_dialog_sound') or self._main_open_dialog_sound)

    def show_question(self, info_id=None, **options):
        options.update({'use_confirm': True})
        self.show_message(info_id, **options)

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
        info_id_list = QuestStringCatalog.get_hint_keys(info_id)
        self._show_next_hint_message(info_id_list)

    def get_initial_message(self):
        return self._initial_msg

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

    def on_key_event(self, event):
        self.key_event = True

    def debug_skip(self):
        skip = self.key_event or self._debug_skip
        self.key_event = None
        self._debug_skip = False
        return skip

    def set_debug_skip(self, debug_skip):
        self._debug_skip = debug_skip

    def __repr__(self):
        return self._name

    def _emit_signal(self, signal_name, *args):
        # The quest runs in a separate thread, but we need to emit the
        # signal from the main one
        GLib.idle_add(self.emit, signal_name, *args)

    def set_cancellable(self, cancellable):
        self._cancellable = cancellable

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
