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
import os
import tempfile

from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.utils import QuestStringCatalog
from clubhouseunittest import ClubhouseTestCase, test_all_episodes, setup_episode


class PhonyQuest(Quest):

    def setup(self):
        self.available = True

    def step_begin(self):
        print('Nothing to see here')


class TestQuestSets(ClubhouseTestCase):

    def setUp(self):
        self.reset_gss()
        Registry.load_current_episode()

    def _get_first_active_quest_set(self, quest_sets, exclude_quest_set):
        for quest_set in quest_sets:
            if quest_set is exclude_quest_set:
                continue
            if quest_set.active:
                return quest_set
        return None

    @test_all_episodes
    def test_questset_contents(self):
        """Tests if any QuestSets are loaded."""
        quest_sets = Registry.get_quest_sets()
        self.assertGreater(len(quest_sets), 0)

    def test_episode_empty_message(self):
        """Tests whether a QuestSet correctly uses the episode's specific NOQUEST messages
        when available.
        """

        class PhonyAlice(QuestSet):
            __pathway_name__ = 'web'
            __character_id__ = 'Alice'

        class PhonyBob(QuestSet):
            __pathway_name__ = 'art'
            __character_id__ = 'Bob'

            def is_active(self):
                return True

        alice = PhonyAlice()
        bob = PhonyBob()

        setup_episode([alice], episode_name='phonyep')

        string_catalog = QuestStringCatalog._csv_dict
        QuestStringCatalog.set_key_value_from_csv_row(('NOQUEST_ALICE_NOTHING',
                                                       'no quest', alice.get_character(),
                                                       'talk', '', ''),
                                                      string_catalog)

        QuestStringCatalog.set_key_value_from_csv_row(('NOQUEST_ALICE_BOB',
                                                       'no quest, check bob', alice.get_character(),
                                                       'talk', '', ''),
                                                      string_catalog)

        # We get any message
        noquest_info = string_catalog['NOQUEST_ALICE_NOTHING']
        ep_noquest_info = noquest_info.copy()
        ep_noquest_info['txt'] = 'ep_noquest_hello'

        noquest_alice_bob_info = string_catalog['NOQUEST_ALICE_BOB']
        ep_noquest_alice_bob_info = noquest_alice_bob_info.copy()
        ep_noquest_alice_bob_info['txt'] = 'check_bob'

        string_catalog.update({'NOQUEST_PHONYEP_ALICE_NOTHING': ep_noquest_info,
                               'NOQUEST_PHONYEP_ALICE_BOB': ep_noquest_alice_bob_info})

        # There's an episode specific noquest message and no other quest-set active.
        self.assertEqual(alice.get_empty_message(), ep_noquest_info['txt'])

        # There's no episode specific noquest message and no other quest-set active.
        del string_catalog['NOQUEST_PHONYEP_ALICE_NOTHING']
        self.assertEqual(alice.get_empty_message(), noquest_info['txt'])

        # There's an episode specific noquest message and an other quest-set active.
        Registry._quest_sets = [alice, bob]
        self.assertEqual(alice.get_empty_message(), ep_noquest_alice_bob_info['txt'])

        # There's no episode specific noquest message and an other quest-set active.
        del string_catalog['NOQUEST_PHONYEP_ALICE_BOB']
        self.assertEqual(alice.get_empty_message(), noquest_alice_bob_info['txt'])

    @test_all_episodes
    def test_empty_message_with_active_questsets(self):
        """Tests the QuestSets empty messages when other QuestSet objects are active."""
        quest_sets = Registry.get_quest_sets()
        quest_sets_to_test = []

        for quest_set in quest_sets:
            # Skip checking the Trap quest set here as it's different.
            if str(quest_set) == 'TrapQuestSet':
                continue

            self.deactivate_quest_set(quest_set)
            quest_sets_to_test.append(quest_set)

        for quest_set in quest_sets_to_test:
            self.check_empty_message_with_active_questsets(quest_sets_to_test, quest_set)

    def activate_quest_set(self, quest_set):
        quest_set.get_quests().insert(0, PhonyQuest(quest_set))
        quest_set.visible = True

    def deactivate_quest_set(self, quest_set):
        quests = quest_set.get_quests()
        if quests:
            if isinstance(quests[0], PhonyQuest):
                del quests[0]

        quest_set.visible = False

    def test_load_mixed_quest_definitions(self):
        '''Tests loading a QuestSet with quests defined as strings and as classes.'''
        quest_set_source = '''
from phonyep.aquest import AQuest
from eosclubhouse.libquest import Registry, QuestSet

class TestQuestSet(QuestSet):
    __pathway_name__ = 'web'
    __character_id__ = 'phony'
    __quests__ = [AQuest, 'ZQuest']

Registry.register_quest_set(TestQuestSet)
'''
        quest_source_template = '''
from eosclubhouse.libquest import Quest
class {}(Quest):
    pass
'''

        with tempfile.TemporaryDirectory() as tmpdir:
            episode_name = 'phonyep'
            dir_name = os.path.join(tmpdir, episode_name)
            os.mkdir(dir_name)

            quest_names = ['AQuest', 'ZQuest']
            for name in quest_names:
                with open(os.path.join(dir_name, name.lower() + '.py'), 'w') as quest_set_file:
                    quest_set_file.write(quest_source_template.format(name))

            # Set the quests for the QuestSet, the first is given as a string, the second as a
            # symbol.
            with open(os.path.join(dir_name, 'testquestset.py'), 'w') as quest_set_file:
                quest_set_file.write(quest_set_source)

            Registry._reset()
            Registry._loaded_episode = episode_name
            Registry.load(dir_name)
            self.assertIn('TestQuestSet',
                          [quest_set.get_id() for quest_set in Registry.get_quest_sets()])
