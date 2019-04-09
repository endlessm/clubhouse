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

    _POWERUP_TYPES = ['invulnerable', 'blowup', 'upgrade']
    _UPGRADE_TYPES = ['shrink', 'attraction']

    _POWERUP_SPAWN_SUFFIX = 'PowerupSpawnCount'
    _POWERUP_PICKED_SUFFIX = 'PowerupPickedCount'
    _POWERUP_ACTIVE_SUFFIX = 'PowerupActivateCount'
    _UPGRADE_ACTIVE_SUFFIX = 'UpgradeActivateCount'

    def __init__(self):
        super().__init__(self.APP_NAME)

        self.POWERUPS_SPAWN_COUNTERS = list(pw + self._POWERUP_SPAWN_SUFFIX
                                            for pw in self._POWERUP_TYPES)

        self.POWERUPS_PICKED_COUNTERS = list(pw + self._POWERUP_PICKED_SUFFIX
                                             for pw in self._POWERUP_TYPES)

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

    def _count_properties(self, type_, suffix, *elements):
        assert all(elem in type_ for elem in elements)
        return sum(self.get_js_property(elem + suffix, 0) for elem in elements)

    def powerups_spawned_count(self, *powerups):
        return self._count_properties(self._POWERUP_TYPES, self._POWERUP_SPAWN_SUFFIX, *powerups)

    def powerups_picked_count(self, *powerups):
        return self._count_properties(self._POWERUP_TYPES, self._POWERUP_PICKED_SUFFIX, *powerups)

    def powerups_active_count(self, *powerups):
        return self._count_properties(self._POWERUP_TYPES, self._POWERUP_ACTIVE_SUFFIX, *powerups)

    def upgrades_active_count(self, *upgrades):
        return self._count_properties(self._UPGRADE_TYPES, self._UPGRADE_ACTIVE_SUFFIX, *upgrades)

    def powerups_spawned(self, *powerups):
        return self.powerups_spawned_count(*powerups) > 0

    def powerups_picked(self, *powerups):
        return self.powerups_picked_count(*powerups) > 0

    def powerups_active(self, *powerups):
        return self.powerups_active_count(*powerups) > 0

    def upgrades_active(self, *upgrades):
        return self.upgrades_active_count(*upgrades) > 0

    def get_powerups_spawned_dict(self, *powerups):
        return {pw: self.powerups_spawned(pw) for pw in powerups}

    def get_powerups_picked_dict(self, *powerups):
        return {pw: self.powerups_picked(pw) for pw in powerups}

    def get_powerups_active_dict(self, *powerups):
        return {pw: self.powerups_active(pw) for pw in powerups}

    def get_upgrades_active_dict(self, *upgrades):
        return {up: self.upgrades_active(up) for up in upgrades}
