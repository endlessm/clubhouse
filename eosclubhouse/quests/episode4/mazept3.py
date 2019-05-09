from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt3(Quest):

    def __init__(self):
        super().__init__('MazePt3', 'ada')
        self._app = Sidetrack()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self._app.set_js_property('availableLevels', ('u', 36))
        if self._app.get_js_property('highestAchievedLevel') > 36:
            self._app.set_js_property('highestAchievedLevel', ('u', 28))
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
            self.dismiss_message()
            self.show_hints_message('RILEYPUSH3_B')
        if current_level == 30:
            self.dismiss_message()
            self.show_hints_message('RILEYPUSH3_C')
        if current_level == 31:
            for i in range(4, 10):
                msgid = 'RILEYPUSH{}'.format(i)
                self.wait_confirm(msgid)
        if current_level == 34:
            self.dismiss_message()
            for message_id in ['DRAMA', 'DRAMA_FELIX', 'DRAMA_FABER', 'DRAMA_RILEY', 'DRAMA_ADA']:
                self.wait_confirm(message_id)
        if current_level == 36:
            for message_id in ['FELIXINTRO', 'FELIXINTRO1', 'FELIXINTRO2', 'FELIXINTRO3']:
                self.wait_confirm(message_id)
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
