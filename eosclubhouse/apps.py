from eosclubhouse.system import App


class LightSpeed(App):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__(self.APP_NAME)

    def set_level(self, level):
        '''Sets the level to be played (starting from 1).'''

        assert level > 0, 'The level should start from 1.'

        levelCount = self.get_js_property('availableLevels')

        if levelCount < level:
            if not self.set_js_property('availableLevels', ('i', level)):
                return False

        return self.set_js_property('nextLevel', ('i', level))
