from eosclubhouse.system import App, GameStateService


class Fizzics(App):

    APP_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__(self.APP_NAME)

        # This is used only for debugging to skip steps:
        self._last_known_level = 0

    def get_current_level(self, debug_skip=False):
        if debug_skip:
            self._last_known_level += 1
            return self._last_known_level

        # The level obtained is zero-based, but this is too confusing
        # because the dialogues are 1-based. So we convert to
        # 1-based here:
        level = self.get_js_property('currentLevel', 0) + 1

        self._last_known_level = level
        return level


class LightSpeed(App):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__(self.APP_NAME)
        self._gss = None

    @property
    def gss(self):
        if self._gss is None:
            self._gss = GameStateService()
        return self._gss

    def set_level(self, level):
        '''Sets the level to be played (starting from 1).'''

        assert level > 0, 'The level should start from 1.'

        levelCount = self.get_js_property('availableLevels')

        if levelCount < level:
            if not self.set_js_property('availableLevels', ('i', level)):
                return False

        return self.set_js_property('startLevel', ('i', level))

    def reveal_topic(self, topic):
        '''Sets a key in the game state so that the given topic ID is revealed
        in Lightspeed's toolbox.'''

        self.gss.set('lightspeed.topic.{}'.format(topic), {'visible': True})
