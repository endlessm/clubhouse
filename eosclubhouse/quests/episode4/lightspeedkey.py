from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import LightSpeed
from eosclubhouse import logger


class LightspeedKey(Quest):

    __available_after_completing_quests__ = ['MazePt1']

    def __init__(self):
        super().__init__('LightspeedKey', 'faber')
        self._app = LightSpeed()

    def step_begin(self):
        # quest starts by clicking on Faber in the clubhouse
        # Faber asks:  LIGHTSPEEDKEY_QUESTION
        # user can reply:  LIGHTSPEEDKEY_QUESTION_ACCEPT  or _ABORT
        # if user does _ACCEPT, then Faber says LIGHTSPEEDKEY_LAUNCH which has _HINT1
        logger.debug('start step_begin')
        self.ask_for_app_launch(self._app, message_id='LIGHTSPEEDKEY_LAUNCH')
        logger.debug('end step_begin')
        return self.step_initiallevel

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_initiallevel(self):
        logger.debug('start step_initiallevel')
        self._app.set_object_property(
            'view.JSContext.globalParameters', 'availableLevels', ('u', 7))
        # self._app.set_js_property('availableLevels', ('u', '7'))
        # for some reason SET_JS_PROPERTY does not work, I need to use the inner function
        # turn on all the topic panels, this will end up changing per-level
        self._app.reveal_topic('spawn')
        self._app.reveal_topic('updateAsteroid')
        self._app.reveal_topic('updateSpinner')
        self._app.reveal_topic('updateSquid')
        self._app.reveal_topic('updateBeam')
        self._app.reveal_topic('activatePowerup')
        self._app.set_level(1)
        logger.debug('end step_initiallevel')
        return self.step_inlevel

    # Decorator can't use self._app since self is not evaluated at function definition time
    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_inlevel(self):
        logger.debug('in step_inlevel, we are somewhere in the game')
        cl = int(self._app.get_js_property('currentLevel', 0))
        logger.debug('currentlevel = ' + str(cl))
        level_id = "LEVELS" + str(cl)
        logger.debug('level_id = ' + str(level_id))
        # there are 5 levels to the Lightspeed quest.  for each level #:
        # at the beginning of the level, Faber says LIGHTSPEEDKEY_LEVELS# which has _HINT1
        # python has no switch statement so we have to do this gross way
        if cl == 0:
            logger.debug('at main menu, do nothing')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_inlevel
        elif cl > 0 and cl < 6:
            self.show_hints_message(level_id)
            self.wait_for_app_js_props_changed(self._app, ['flipped', 'currentLevel'])
            if self._app.get_js_property('flipped'):
                return self.step_incode
            elif self._app.get_js_property('currentLevel', 0) != cl:
                return self.step_inlevel
            else:
                logger.warning(
                    'Unexpected State - Flipped or currentlevel changed, but both checks failed!')
                return self.step_inlevel
        else:
            return self.step_success

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_incode(self):
        logger.debug('in step_incode, should be in the code panel')

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
        logger.debug('in step_success, should be still in Lightspeed but playing victory dialogue')
        # when the user beats level 5, Faber says LIGHTSPEEDKEY_SUCCESS
        self.wait_confirm('SUCCESS')
        # give the player the key: Riley Maze Instructions Panel
        # items are stored in the text spreadsheet
        self.give_item('item.reward.testreward')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
