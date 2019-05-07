from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack
from eosclubhouse import logger


class MazePt3(Quest):

    def __init__(self):
        super().__init__('MazePt3', 'ada')
        self._app = Sidetrack()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self._app.set_js_property('availableLevels', ('u', 36))
        logger.debug('available levels = %i', int(self._app.get_js_property('currentLevel')))
        return self.step_play_level

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 28:
            # this set of lines needs to be reorganized
            self.show_hints_message('RILEYPUSH')
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
            self.wait_confirm('RILEYPUSH2')
            self.wait_confirm('RILEYPUSH3')
        if current_level == 29:
            self.show_hints_message('RILEYPUSH3_B')
        if current_level == 30:
            self.show_hints_message('RILEYPUSH3_C')
        if current_level == 31:
            self.wait_confirm('RILEYPUSH4')
            self.wait_confirm('RILEYPUSH5')
            self.wait_confirm('RILEYPUSH6')
            self.wait_confirm('RILEYPUSH7')
            self.wait_confirm('RILEYPUSH8')
            self.wait_confirm('RILEYPUSH9')
        if current_level == 34:
            self.show_hints_message('DRAMA')
            self.show_hints_message('DRAMA_FELIX')
            self.show_hints_message('DRAMA_FABER')
            self.show_hints_message('DRAMA_RILEY')
            self.show_hints_message('DRAMA_ADA')
        if current_level == 36:
            self.wait_confirm('FELIXINTRO')
            self.wait_confirm('FELIXINTRO1')
            self.wait_confirm('FELIXINTRO2')
            self.wait_confirm('FELIXINTRO3')
            # wait for failure
            self.wait_for_app_js_props_changed(self._app, ['success'])
            self.wait_confirm('FELIXINTRO_FAILURE')
            return self.step_success
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_play_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
