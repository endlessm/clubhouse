from eosclubhouse.libquest import Registry, Quest
from eosclubhouse.utils import QS
from clubhouseunittest import ClubhouseTestCase, test_all_episodes


class PhonyQuest(Quest):

    def __init__(self, quest_set):
        super().__init__('PhonyQuest for {}'.format(quest_set), quest_set.get_character())
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
    def test_empty_message_with_inactive_questsets(self):
        """Tests the QuestSets empty messages when other QuestSets are inactive."""
        quest_sets = Registry.get_quest_sets()
        for quest_set in quest_sets:
            self.deactivate_quest_set(quest_set)

        for quest_set in quest_sets:
            message = quest_set.get_empty_message()

            noquest_msg_id = 'NOQUEST_{}_NOTHING'.format(quest_set.get_character())
            expected_message = QS(noquest_msg_id.upper())

            self.assertEqual(message, expected_message)

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

    def check_empty_message_with_active_questsets(self, quest_sets, test_quest_set):
        # Activate one quest set at a time and verify that the NOQUEST message matches the one
        # for quest set.
        for quest_set in quest_sets:
            if quest_set is test_quest_set:
                continue

            self.activate_quest_set(quest_set)

            empty_message = test_quest_set.get_empty_message()

            self.deactivate_quest_set(quest_set)

            noquest_msg_id = 'NOQUEST_{}_{}'.format(test_quest_set.get_character(),
                                                    quest_set.get_character())

            message = QS(noquest_msg_id.upper())

            quest_set.active = False

            self.assertEqual(empty_message, message,
                             'Failed while checking empty message from {} for '
                             'active {}'.format(test_quest_set, quest_set))
