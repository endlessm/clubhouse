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

import pkgutil
import sys

from eosclubhouse import logger
from gi.repository import GObject, GLib


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
            GObject.SignalFlags.RUN_FIRST, None, (str, str)
        ),
        'question': (
            GObject.SignalFlags.RUN_FIRST, None, (str, GObject.TYPE_PYOBJECT, str)
        ),
    }

    def __init__(self, name, main_character_id, initial_msg):
        super().__init__()
        self._name = name
        self._initial_msg = initial_msg
        self._characters = {}
        self._main_character_id = main_character_id

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

    def __repr__(self):
        return self._name

    def _emit_signal(self, signal_name, *args):
        # The quest runs in a separate thread, but we need to emit the
        # signal from the main one
        GLib.idle_add(self.emit, signal_name, *args)
