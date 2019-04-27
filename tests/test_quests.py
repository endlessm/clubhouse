from eosclubhouse.libquest import Registry, Quest, QuestSet, NoMessageIdError
from eosclubhouse.utils import QuestStringCatalog
from clubhouseunittest import ClubhouseTestCase


class PhonyQuest(Quest):

    def __init__(self, quest_set):
        super().__init__('PhonyQuest for {}'.format(quest_set), quest_set.get_character())
        self.available = True

    def step_begin(self):
        print('Nothing to see here')


class TestQuests(ClubhouseTestCase):

    def setUp(self):
        Registry.load_current_episode()

    def test_show_message_can_raise_custom_error(self):
        """Tests that Quests raise a custom error when a message ID is not in the catalog."""

        class PhonyAlice(QuestSet):
            __character_id__ = 'Alice'

        quest = PhonyQuest(PhonyAlice)

        string_catalog = QuestStringCatalog._csv_dict
        QuestStringCatalog.set_key_value_from_csv_row(('PHONYQUEST_HELLO',
                                                       '', '', '', '', ''),
                                                      string_catalog)

        # The short and full forms should not raise:
        quest.show_message('HELLO')
        quest.show_message('PHONYQUEST_HELLO')

        with self.assertRaises(NoMessageIdError):
            quest.show_message('INEXISTENT_MESSAGE')
