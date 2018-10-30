import time

from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada', QS('FIZZICSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._go_next_step = False

    def start(self):
        self.set_keyboard_request(True)

        dt = 1
        time_in_step = 0
        starting = True
        step_func = self.step_first

        while True:
            new_func = step_func(step_func, starting, time_in_step)
            if new_func is None:
                break
            elif new_func != step_func:
                step_func = new_func
                time_in_step = 0
                starting = True
            else:
                time.sleep(dt)
                time_in_step += dt
                starting = False

    def go_next_step(self):
        self._go_next_step = True

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIZZICSINTRO_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

        return step

    # STEP 1
    def step_explanation(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('FIZZICSINTRO_EXPLANATION'),
                               choices=[('OK', self.go_next_step)])
        if (self._go_next_step):
            self._go_next_step = False
            return self.step_ricky
        return step

    def step_ricky(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('FIZZICSINTRO_RICKY'),
                               choices=[('OK', self.go_next_step)], character_id='ricky')
        if (self._go_next_step):
            self._go_next_step = False
            return self.step_intro
        return step

    def step_intro(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('FIZZICSINTRO_INTRO'),
                               choices=[('OK', self.go_next_step)])
        if (self._go_next_step):
            self._go_next_step = False
            return self.step_reward
        return step

    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.conf['complete'] = True
            self.available = False
