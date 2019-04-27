from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt1(Quest):

    __available_after_completing_quests__ = ['TrapIntro']

    def __init__(self):
        super().__init__('MazePt1', 'ada')
        self._app = Sidetrack()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')
        self._app.set_js_property('availableLevels', ('u', 26))
        self.wait_confirm('RILEYHELLO')
        self.wait_confirm('EXIT')
        return self.step_play_level

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 0:
            # in menu, do nothing
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_play_level
        elif current_level > 0 and current_level < 5:
            msg_id = 'MANUAL' + str(current_level)
            if current_level == 2 or current_level == 3:
                self.wait_confirm(msg_id)
            else:
                self.show_hints_message(msg_id)
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            # self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'success'])
            # if not self._app.get_js_property('success'):
            #     self.wait_confirm('DIED_RESTART')
            return self.step_play_level
        elif current_level == 14:
            self.wait_confirm('AUTO1')
            self.pause(7)
            self.wait_confirm('AUTO1_FELIX')
            self.wait_confirm('AUTO1_FABER')
            self.wait_confirm('AUTO1_ADA')
            self.wait_confirm('AUTO1_RILEY')
            self.show_hints_message('AUTO1_SANIEL')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_play_level
        elif current_level == 15:
            self.show_hints_message('AUTO2')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_play_level
        elif current_level == 16:
            self.show_hints_message('AUTO3')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            self.wait_confirm('AUTO3_SUCCESS')
            self.pause(3)
            return self.step_play_level
        elif current_level == 17:
            self.wait_confirm('AUTO4_BACKSTORY')
            self.wait_confirm('AUTO4_BACKSTORY2')
            self.pause(3)
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_play_level
        elif current_level == 25:
            self.wait_confirm('AUTO5')
            self.show_hints_message('AUTO5_ADA')
            # self.wait_for_app_js_props_changed(self._app, ['success'])
            self.pause(7)
            self.wait_confirm('AUTO5_FAILURE_ADA')
            self.wait_confirm('AUTO5_FAILURE_ADA2')
            return self.step_success
        else:
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_play_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
