from eosclubhouse.libquest import Registry, NoMessageIdError
from eosclubhouse.utils import QuestStringCatalog
from clubhouseunittest import ClubhouseTestCase, define_quest, define_quest_set, setup_episode


class TestQuests(ClubhouseTestCase):

    def setUp(self):
        Registry.load_current_episode()

    def test_show_message_can_raise_custom_error(self):
        """Tests that Quests raise a custom error when a message ID is not in the catalog."""

        quest = define_quest('PhonyQuest', 'Alice')()

        string_catalog = QuestStringCatalog._csv_dict
        QuestStringCatalog.set_key_value_from_csv_row(('PHONYQUEST_HELLO',
                                                       '', '', '', '', ''),
                                                      string_catalog)

        # The short and full forms should not raise:
        quest.show_message('HELLO')
        quest.show_message('PHONYQUEST_HELLO')

        with self.assertRaises(NoMessageIdError):
            quest.show_message('INEXISTENT_MESSAGE')

    def test_verify_dependencies(self):
        """Tests that Quests compute their dependencies correctly, taking into account the
        quests coming before them in the QuestSet but also their own dependencies."""

        def get_dependencies(quest_id):
            quest = Registry.get_quest_by_name(quest_id)
            return [quest_dep.get_id() for quest_dep in quest.get_dependency_quests()]

        PhonyAlice = define_quest_set('PhonyAlice', 'Alice',
                                      [('QuestA0', []),
                                       ('QuestB0', []),
                                       ('QuestC0', []),
                                       ('QuestD0', ['QuestB1'])])

        PhonyBob = define_quest_set('PhonyBob', 'Bob',
                                    [('QuestA1', []),
                                     ('QuestB1', ['QuestC0'])])

        setup_episode([PhonyAlice(), PhonyBob()])

        self.assertEqual(get_dependencies('QuestD0'),
                         ['QuestC0', 'QuestB0', 'QuestA0', 'QuestB1', 'QuestA1'])

        self.assertEqual(get_dependencies('QuestB1'), ['QuestA1', 'QuestC0', 'QuestB0', 'QuestA0'])

        self.assertEqual(get_dependencies('QuestC0'), ['QuestB0', 'QuestA0'])

        self.assertEqual(get_dependencies('QuestA1'), [])

    def test_main_character(self):
        '''Tests what the main character is when quests are initialized.'''
        QuestA = define_quest('QuestA')

        PhonyAlice = define_quest_set('PhonyAlice', 'alice')
        PhonyAlice.__quests__ = [QuestA]

        setup_episode([PhonyAlice()])

        quest_a = Registry.get_quest_by_name('QuestA')
        self.assertEqual(quest_a.get_main_character(), 'alice')

    def test_proposal_message_id(self):
        '''Tests overriding the proposal message ID of quests.'''
        a_proposal = 'a quest question'
        b_proposal = 'b quest welcome'

        string_catalog = QuestStringCatalog._csv_dict
        QuestStringCatalog.set_key_value_from_csv_row(('QUESTA_QUESTION',
                                                       a_proposal, 'alice',
                                                       'talk', '', ''),
                                                      string_catalog)
        QuestStringCatalog.set_key_value_from_csv_row(('QUESTB_WELCOME',
                                                       b_proposal, 'bob',
                                                       'talk', '', ''),
                                                      string_catalog)

        QuestA = define_quest('QuestA', 'alice')
        QuestB = define_quest('QuestB', 'bob')
        QuestB.__proposal_message_id__ = 'WELCOME'

        PhonySet = define_quest_set('PhonySet', 'alice')
        PhonySet.__quests__ = [QuestA, QuestB]

        setup_episode([PhonySet()])

        quest_a = Registry.get_quest_by_name('QuestA')
        self.assertEqual(quest_a.proposal_message, a_proposal)

        quest_b = Registry.get_quest_by_name('QuestB')
        self.assertEqual(quest_b.proposal_message, b_proposal)
