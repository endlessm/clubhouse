from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import LightSpeed
from eosclubhouse import logger


class LightspeedKey(Quest):

    __available_after_completing_quests__ = ['MazePt1']

    FIRST_LEVEL = 15
    LAST_LEVEL = 17

    def __init__(self):
        super().__init__('LightspeedKey', 'faber')
        self._app = LightSpeed()

    def step_begin(self):
        self.ask_for_app_launch(self._app, message_id='LIGHTSPEEDKEY_LAUNCH')
        return self.step_initiallevel

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_initiallevel(self):
        self._app.set_object_property(
            'view.JSContext.globalParameters', 'availableLevels', ('u', 7))
        # self._app.set_js_property('availableLevels', ('u', '7'))
        # for some reason SET_JS_PROPERTY does not work, I need to use the inner function
        # turn on all the topic panels, this will end up changing per-level
        self._app.reveal_topic('spawn')
        self._app.set_topic_sensitive('spawn', False)
        self._app.reveal_topic('updateAsteroid')
        self._app.reveal_topic('updateSpinner')
        self._app.reveal_topic('updateSquid')
        self._app.reveal_topic('updateBeam')
        self._app.reveal_topic('activatePowerup')
        self._app.set_level(self.FIRST_LEVEL)
        return self.step_inlevel

    # Decorator can't use self._app since self is not evaluated at function definition time
    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_inlevel(self):
        current_level = self._app.get_js_property('currentLevel', 0)
        level_id = "LEVELS{}".format(int(current_level - self.FIRST_LEVEL + 1))
        # there are 5 levels to the Lightspeed quest.  for each level #:
        # at the beginning of the level, Faber says LIGHTSPEEDKEY_LEVELS# which has _HINT1
        # python has no switch statement so we have to do this gross way
        if current_level == 0:
            logger.debug('at main menu, do nothing')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_inlevel
        elif self.FIRST_LEVEL <= current_level <= self.LAST_LEVEL:
            self.show_hints_message(level_id)
            self.wait_for_app_js_props_changed(self._app, ['flipped', 'currentLevel'])
            if self._app.get_js_property('flipped'):
                return self.step_incode
            elif self._app.get_js_property('currentLevel', 0) != current_level:
                return self.step_inlevel
            else:
                logger.warning(
                    'Unexpected State - Flipped or currentlevel changed, but both checks failed!')
                return self.step_inlevel
        else:
            return self.step_success

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_incode(self):
        # waiting for new hooks and functionality here
        #
        # if the user flips the app and clicks on a coding panel, Faber responds as follows:
        # LIGHTSPEEDKEY_PANEL_LOCKED - if the panel they've clicked on is not available this level
        # LIGHTSPEEDKEY_PANEL_GAME- if they click on the Game panel
        # LIGHTSPEEDKEY_PANEL_SPAWN - if they click on the Spawn panel
        # LIGHTSPEEDKEY_PANEL_ASTEROID - if they click on the Asteroid panel
        # LIGHTSPEEDKEY_PANEL_SPINNER - if they click on the Spinner panel
        # LIGHTSPEEDKEY_PANEL_SQUID - if they click on the Squid panel
        # LIGHTSPEEDKEY_PANEL_BEAM - if they click on the Beam panel
        # LIGHTSPEEDKEY_PANEL_POWERUPS - if they click on the PowerUps panel

        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_inlevel

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.give_item('item.key.sidetrack.1')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
