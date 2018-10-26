import time

from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class Roster(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'

    def __init__(self):
        super().__init__('Roster', 'ada', QS('ROSTER_QUESTION'))
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
            self.show_question(QS('ROSTER_PRELAUNCH'),
                               choices=[('OK', self.go_next_step)])

        if (self._go_next_step):
            self._go_next_step = False
            return self.step_launch

        return step

    # STEP 1
    def step_launch(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('ROSTER_LAUNCH'))
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

        return step

    # STEP 2
    def step_explanation(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('ROSTER_EXPLANATION'))
            self.conf['complete'] = True
            self.available = False

        if time_in_step > 5:
            return

        return step
