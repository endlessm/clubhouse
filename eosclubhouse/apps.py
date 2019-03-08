from eosclubhouse.system import App, GameStateService


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
