from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack
from eosclubhouse import logger


class MazePt2(Quest):

    __available_after_completing_quests__ = ['LightspeedKey']

    def __init__(self):
        super().__init__('MazePt2', 'ada')
        self._app = Sidetrack()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self._app.set_js_property('availableLevels', ('u', 28))
        logger.debug('available levels = %i', int(self._app.get_js_property('currentLevel')))
        return self.step_play_level

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 23:
            self.show_hints_message('FLIP')
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
            self.show_hints_message('INSTRUCTIONS')
        elif current_level == 24:
            self.show_hints_message('LEVELS2')
        elif current_level == 25:
            self.show_hints_message('FIXANDREORDER')
            self.pause(7)
            self.show_hints_message('FIXANDREORDER_FIXED')
        elif current_level == 26:
            # hackdex here?
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            self.wait_confirm('RESEARCH1')
            self.wait_confirm('RESEARCH2')
            return self.step_play_level
        elif current_level == 28:
            # we can't have decrypted the hackdex yet
            self.wait_confirm('IMPASSABLE')
            self.wait_confirm('IMPASSABLE_FABER')
            self.wait_confirm('IMPASSABLE_RILEY')
            return self.step_success
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_play_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
