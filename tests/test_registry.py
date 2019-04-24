from eosclubhouse.libquest import Registry
from eosclubhouse import config
from clubhouseunittest import ClubhouseTestCase


class TestRegistry(ClubhouseTestCase):

    def test_default_episode(self):
        Registry.load_current_episode()
        self.assertEqual(Registry.get_loaded_episode_name(), config.DEFAULT_EPISODE_NAME)
