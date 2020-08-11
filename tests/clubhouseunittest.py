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
import copy
import unittest

from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.system import GameStateService
from eosclubhouse.utils import QuestStringCatalog
from gi.repository import Gio, GObject
from unittest import mock


class _GSSMockProxy(GObject.GObject):

    __state__ = {}

    __gsignals__ = {
        'g-signal': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str, GObject.TYPE_VARIANT)
        ),
    }

    def call(self, method_name, variant, _flags, _timeout, _param, done_callback):
        method = getattr(self, method_name)

        method(variant.format_string, variant.get_child_value(0), variant.get_child_value(1))

        done_callback(self, None)

    def Get(self, _variant_format, key):
        try:
            return self.__state__[key]
        except KeyError:
            raise Gio.DBusError.new_for_dbus_error("com.hack_computer.GameStateService.KeyError",
                                                   "Phony KeyError")

    def Set(self, _variant_format, key, variant):
        self.__state__[key] = variant.unpack()
        self.emit('g-signal', 'phony', 'changed', None)

    def Reset(self):
        self.__state__ = {}

    def call_finish(self, _param):
        pass


class ClubhouseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the GSS doesn't affect the real game state.
        GameStateService._proxy = _GSSMockProxy()

        # Also patch set_async() with set() to simplify testing:
        GameStateService.set_async = GameStateService.set

        # Reset the GSS so every test case starts with a clean slate.
        cls.reset_gss()

        # We patch the QuestStringCatalog so any changes made by a test aren't kept in the string
        # catalog for the next test or beyond tests. We patch the catalog with a deep copy of it
        # since otherwise only the dictionary is "protected" but not its members (so if a test
        # changes a message's sound, it'd remain like that even with the mock patch).
        strings_catalog_copy = copy.deepcopy(QuestStringCatalog._csv_dict)
        mock.patch.dict('eosclubhouse.utils.QuestStringCatalog._csv_dict',
                        strings_catalog_copy, clear=True).start()

    @classmethod
    def tearDownClass(cls):
        # Stop any mock patches created in the setUpClass.
        mock.patch.stopall()

    @classmethod
    def reset_gss(self):
        GameStateService().reset()


def test_all_episodes(skip=[]):

    def decorator(function):

        def test_on_episodes(*args, **kwargs):
            episodes = Registry.get_available_episodes()

            for episode in episodes:
                if episode in skip:
                    continue

                # Load the next episode.
                Registry.set_current_episode(episode)
                Registry.load_current_episode()

                try:
                    # Call the test method.
                    function(*args, **kwargs)
                except Exception:
                    # Inform about which episode failed and propagate the failure.
                    print('Failed test in episode "{}"'.format(episode))
                    raise

        return test_on_episodes

    return decorator


def define_quest(quest_id, available_after=[]):
    def step_begin(self):
        print('Nothing to see here!')

    return type(quest_id, (Quest,), {'__available_after_completing_quests__': available_after,
                                     'step_begin': step_begin})


def define_questset(quest_set_id, pathway_name, character_id, quest_id_deps_list=[]):
    quests = []
    for quest_id, dependencies in quest_id_deps_list:
        quests.append(define_quest(quest_id, dependencies))

    return type(quest_set_id, (QuestSet,), {'__quests__': quests,
                                            '__pathway_name__': pathway_name,
                                            '__character_id__': character_id})


def setup_episode(quest_set_list, episode_name='tests-phony-episode'):
    Registry._reset()
    Registry._quest_sets = quest_set_list
    Registry._loaded_episode = episode_name
