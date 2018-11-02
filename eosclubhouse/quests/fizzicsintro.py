from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada', QS('FIZZICSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._go_next_step = False

    def go_next_step(self):
        self._go_next_step = True

    def check_next_step(self):
        go_next_step = self._go_next_step
        self._go_next_step = False
        return go_next_step

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICSINTRO_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

        return None

    # STEP 1
    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_EXPLANATION'),
                               choices=[('OK', self.go_next_step)])
        if self.check_next_step():
            return self.step_ricky

        return None

    def step_ricky(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_RICKY'),
                               choices=[('OK', self.go_next_step)], character_id='ricky')
        if self.check_next_step():
            return self.step_intro

        return None

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question(QS('FIZZICSINTRO_INTRO'),
                               choices=[('OK', self.go_next_step)])
        if self.check_next_step():
            return self.step_reward

        return None

    def step_reward(self, time_in_step):
        self.stop()
        return None
