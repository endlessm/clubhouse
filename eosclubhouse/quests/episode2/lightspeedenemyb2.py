from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class LightSpeedEnemyB2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyB2', 'saniel')
        self._app = App(self.APP_NAME)

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_explanation
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_delay

    def step_delay(self, time_in_step):
        if time_in_step >= 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('EXPLAIN')
        if self.debug_skip():
            return self.step_success

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question('SUCCESS')
        if self.confirmed_step():
            self.give_item('item.stealth.2')
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('END', confirm_label='Bye')
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
