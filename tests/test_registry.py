from eosclubhouse.libquest import Registry
from eosclubhouse import config
from clubhouseunittest import ClubhouseTestCase, test_all_episodes


class TestRegistry(ClubhouseTestCase):

    def test_default_episode(self):
        Registry.load_current_episode()
        self.assertEqual(Registry.get_loaded_episode_name(), config.DEFAULT_EPISODE_NAME)

    @test_all_episodes
    def test_episode_completion_fraction(self):
        '''Checks the Registry.get_current_episode_progress() method'''
        def _compare_completion_quests(quest):
            return 1 if quest.__complete_episode__ else 0

        quests = sorted(Registry.get_current_quests(), key=_compare_completion_quests)

        def _complete_quest(quest, complete=True):
            quest.complete = complete
            print('::::', quest.__complete_episode__)
            return complete

        # Set all quests as not completed
        list(map(lambda quest: _complete_quest(quest, False), quests))
        self.assertEqual(Registry.get_current_episode_progress(), 0)

        # Set only one quest as not completed
        quests[0].complete = True
        self.assertGreater(Registry.get_current_episode_progress(), 0)

        # Set half of the quests as completed (if we have more than 1 quest)
        if len(quests) > 1:
            list(map(_complete_quest, quests[:len(quests) // 2]))
            self.assertAlmostEqual(Registry.get_current_episode_progress(), .5, delta=.1)

        # Set all quests as completed
        list(map(_complete_quest, quests))
        self.assertEqual(Registry.get_current_episode_progress(), 1)
