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

import os
import pkgutil
import sys

from eosclubhouse import config, logger
from gi.repository import GObject


class Registry:

    _quests = []

    @staticmethod
    def load(quest_folder):
        sys.path.append(quest_folder)

        for _unused, modname, _unused in pkgutil.walk_packages([quest_folder]):
            __import__(modname)

        del sys.path[sys.path.index(quest_folder)]

    @classmethod
    def register_quest(class_, quest_class):
        logger.info('Quest registered: %s', quest_class)
        if not issubclass(quest_class, Quest):
            raise TypeError('{} is not a of type {}'.format(quest_class, Quest))
        quest = quest_class()
        class_._quests.append(quest)

    @classmethod
    def get_quests(class_):
        return class_._quests


class Quest(GObject.GObject):

    __gsignals__ = {
        'message': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str,)
        ),
        'question': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str, GObject.TYPE_PYOBJECT)
        ),
    }

    def __init__(self, name, main_character_id, initial_msg):
        super().__init__()
        self._name = name
        self._initial_msg = initial_msg
        self._characters = {}
        self._main_character = self.get_character(main_character_id)

    def start(self):
        raise NotImplementedError()

    def get_main_character(self):
        return self._main_character

    def get_character(self, character_id):
        character = self._characters.get(character_id)

        if character is None:
            character = Character(self, character_id)
            self._characters[character_id] = character

        return character

    def show_message(self, txt, character=None, mood=None):
        character = character or self._main_character
        if mood is not None:
            character.mood = mood
        self.emit('message', character.name, txt)

    def show_question(self, txt, choices, character=None, mood=None):
        character = character or self._main_character
        if mood is not None:
            character.mood = mood

        possible_answers = [(text, callback) for text, callback in choices]

        self.emit('question', character.name, txt, possible_answers)

    def get_initial_message(self):
        return self._initial_msg

    def __repr__(self):
        return self._name


class Character(GObject.GObject):

    def __init__(self, quest, id_, name=None):
        super().__init__()
        self._quest = quest
        self._id = id_
        self._name = name or id_
        self.load()

    def show_message(self, txt):
        self._quest.show_message()

    def _get_name(self):
        return self._name

    def get_image_path(self):
        return self._moods.get(self.mood)

    def load(self):
        char_dir = os.path.join(config.CHARACTERS_DIR, self._id)
        self._moods = {}
        for image in os.listdir(char_dir):
            name, ext = os.path.splitext(image)
            path = os.path.join(char_dir, image)
            self._moods[name] = path

        # @todo: Raise exception here instead
        assert(self._moods)

        if 'normal' in self._moods.keys():
            self.mood = 'normal'
        else:
            self.mood = self._moods.keys()[0]

    name = property(_get_name)
    mood = GObject.Property(type=str)
