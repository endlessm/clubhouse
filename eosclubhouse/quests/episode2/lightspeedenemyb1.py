from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class LightSpeedEnemyB1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyB1', 'saniel')
        self._app = App(self.APP_NAME)

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_level
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_delay

    def step_delay(self, time_in_step):
        if time_in_step >= 2:
            return self.step_level

    def step_level(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('LEVEL')
        if self.debug_skip():
            return self.step_code

    def step_code(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE')
        if self.debug_skip():
            return self.step_code2

    def step_code2(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE2')
        if self.debug_skip():
            return self.step_play

    def step_play(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('PLAY')
        if self.debug_skip():
            return self.step_code3

    def step_code3(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE3')
        if self.debug_skip():
            return self.step_play2

    def step_play2(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('PLAY2')
        if self.debug_skip():
            return self.step_code4

    def step_code4(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE4')
        if self.debug_skip():
            return self.step_success

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('SUCCESS', confirm_label='Bye')
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
