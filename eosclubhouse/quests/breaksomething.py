import time

from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class BreakSomething(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Break Something', 'ricky', QS('BREAK_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._go_next_step = False
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

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

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if (self.is_named_quest_complete("OSIntro")):
            self.available = True

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('BREAK_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

        return step

    # STEP 1
    def step_explanation(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('BREAK_OSAPP'))

        # TODO: Wait for flip to hack
        if self.debug_skip():
            return self.step_unlock

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        return step

    def step_unlock(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('BREAK_UNLOCK'))

        # TODO: Wait for unlock
        if self.debug_skip():
            return self.step_unlocked
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        return step

    def step_unlocked(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('BREAK_UNLOCKED'))

        # TODO: Wait for goal to be met (large cursor)
        if self.debug_skip():
            return self.step_success
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        return step

    def step_success(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('BREAK_SUCCESS'),
                               choices=[('OK', self.go_next_step)])
        if (self._go_next_step):
            self._go_next_step = False
            return self.step_reset
        return step

    def step_reset(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('BREAK_ARCHIVISTARRIVES'), character_id='archivist')

        # TODO: Wait for goal to be met (reset button)
        if self.debug_skip():
            return self.step_reward

        return step

    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('BREAK_WRAPUP'), choices=[('OK', self.go_next_step)],
                               character_id='archivist')
            self.conf['complete'] = True
            self.available = False

        if self._go_next_step:
            self._go_next_step = False
            return self.step_end

        return step

    def step_end(self, step, starting, time_in_step):
        return

    # STEP Abort
    def step_abort(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('BREAK_ABORT'))

        if time_in_step > 5:
            return

        return step
