from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Hackdex2Decrypt(Quest):

    APP_NAME = 'com.endlessm.Hackdex2'

    def __init__(self):
        super().__init__('Hackdex2Decrypt', 'riley')
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
            self.show_hints_message('EXPLANATION')
        if self.debug_skip():
            return self.step_hack

    def step_hack(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('HACK')
        if self.debug_skip():
            return self.step_success

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('SUCCESS', confirm_label='Bye')
        if self.confirmed_step():
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
