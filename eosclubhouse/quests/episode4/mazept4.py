from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, GameStateService
from eosclubhouse.apps import Sidetrack
from eosclubhouse import logger


class MazePt4(Quest):

    __available_after_completing_quests__ = ['FizzicsKey']
    __complete_episode__ = True

    def __init__(self):
        super().__init__('MazePt4', 'ada')
        self._gss = GameStateService()
        self._app = Sidetrack()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self._app.set_js_property('availableLevels', ('u', 40))
        logger.debug('available levels = %i', int(self._app.get_js_property('availableLevels')))
        return self.step_play_level

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 36:
            self.show_hints_message('FLIP')
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
            self.show_hints_message('UNITS')
        if current_level == 37:
            self.wait_confirm('LEVELS2')
        if current_level == 38:
            self.wait_confirm('LEVELS3')
        if current_level == 39:
            self.wait_confirm('LEVELS4')
            self.wait_confirm('LEVELS4_SANIEL')
        if current_level == 40:
            self.wait_confirm('LEVELS5')
            self.wait_confirm('LEVELS5_RILEY')
            self.wait_confirm('LEVELS5_SANIEL')
            # user finishes level
            self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'success'])
            if not self._app.get_js_property('success'):
                return self.step_play_level
            else:
                # felix escapes!
                self._app.set_js_property('escapeCutscene', ('b', True))
                logger.debug("started escape cutscene")
                self.pause(1)
                self.wait_for_app_js_props_changed(self._app, ['escapeCutscene'])
                logger.debug("detected cutscene state change")
                self.wait_confirm('END1')
                self.wait_confirm('END2')
                self.wait_confirm('END3')
                self.wait_confirm('END4')
                return self.step_success
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_play_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        # Yay riley's back
        self._gss.set('clubhouse.character.Riley', {'in_trap': False})
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
