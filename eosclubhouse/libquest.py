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

import inspect
import json
import os
import pkgutil
import sys

from eosclubhouse import logger
from gi.repository import GObject, GLib


class Registry:

    _quests = []
    _quest_sets = []

    @staticmethod
    def load(quest_folder):
        sys.path.append(quest_folder)

        for _unused, modname, _unused in pkgutil.walk_packages([quest_folder]):
            __import__(modname)

        del sys.path[sys.path.index(quest_folder)]

    # @todo: This method should be removed. It's only here for convenience in case the
    # quest writer has already some quests locally that are registered with this method
    @classmethod
    def register_quest(class_, quest_class):
        if not issubclass(quest_class, Quest):
            raise TypeError('{} is not a of type {}'.format(quest_class, Quest))
        quest = quest_class()
        new_quest_set = type(quest_class.__name__ + 'QuestSet',
                             (QuestSet,),
                             {'__quests__': [quest],
                              '__charachter_id__': quest.get_main_character()})
        new_quest_set.add_quest(quest_class)
        class_.register_quest_set(new_quest_set)
        logger.info('QuestSet %s automatically created for: %s', new_quest_set, quest_class)

    @classmethod
    def register_quest_set(class_, quest_set):
        if not issubclass(quest_set, QuestSet):
            raise TypeError('{} is not a of type {}'.format(quest_set, QuestSet))
        class_._quest_sets.append(quest_set())
        logger.info('QuestSet registered: %s', quest_set)

    @classmethod
    def get_quests(class_):
        return class_._quests

    @classmethod
    def get_quest_sets(class_):
        return class_._quest_sets


class Quest(GObject.GObject):

    __gsignals__ = {
        'message': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str)
        ),
        'question': (
            GObject.SignalFlags.RUN_FIRST, None, (str, GObject.TYPE_PYOBJECT, str)
        ),
        'key-events-request': (
            GObject.SignalFlags.RUN_FIRST, None, (bool,)
        )
    }

    def __init__(self, name, main_character_id, initial_msg):
        super().__init__()
        self._name = name
        self._initial_msg = initial_msg
        self._characters = {}
        self._main_character_id = main_character_id
        self._cancellable = None
        self.load_conf()

    def start(self):
        raise NotImplementedError()

    def get_main_character(self):
        return self._main_character_id

    def show_message(self, txt, character_id=None, mood=None):
        self._emit_signal('message', txt, mood)

    def show_question(self, txt, choices, character_id=None, mood=None):
        possible_answers = [(text, callback) for text, callback in choices]

        self._emit_signal('question', txt, possible_answers, mood)

    def get_initial_message(self):
        return self._initial_msg

    def set_keyboard_request(self, wants_keyboard_events):
        self._emit_signal('key-events-request', wants_keyboard_events)

    def on_key_event(self, event):
        pass

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
    def _get_conf_file_path(class_):
        return os.path.join(GLib.get_user_config_dir(), class_.__name__)

    def load_conf(self):
        conf_path = self._get_conf_file_path()
        if not os.path.exists(conf_path):
            self.conf = {}
            return

        with open(conf_path, 'r') as conf_file:
            self.conf = json.load(conf_file)

    def save_conf(self):
        conf_path = self._get_conf_file_path()
        with open(conf_path, 'w') as conf_file:
            json.dump(self.conf, conf_file)

    def set_conf(self, key, value):
        self.conf[key] = value

    def get_conf(self, key):
        return self.conf.get(key)


class QuestSet(GObject.GObject):

    __quests__ = []
    # @todo: Default character; should be set to None in the future
    __character_id__ = 'aggretsuko'
    __position__ = (0, 0)

    def __init__(self):
        super().__init__()
        self._position = self.__position__

    @classmethod
    def get_character(class_):
        return class_.__character_id__

    @classmethod
    def add_quest(class_, quest):
        if inspect.isclass(quest):
            new_quest = quest()
        else:
            new_quest = quest
        class_.__quests__.append(new_quest)

    @classmethod
    def get_quests(class_):
        return class_.__quests__

    def get_next_quest(self):
        quests = self.get_quests()
        return quests[0] if quests else None

    def get_position(self):
        return self._position
