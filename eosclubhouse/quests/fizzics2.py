import time

from gi.repository import GLib
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class Fizzics2(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackyballs'

    def __init__(self):
        super().__init__('Fizzics 2', 'ricky', QS('FIZZICS2_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._initialized = False
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
            self.show_message(QS('FIZZICS2_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_wait_score

        if (time_in_step > 20 and not self._hint0):
            self.show_message(QS('FIZZICS2_HINT1'))
            self._hint0 = True

        return step

    # STEP 1
    def step_wait_score(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIZZICS2_GOAL'))

        if time_in_step < 3:
            return step

        try:
            if not self._initialized:
                self._app.set_object_property('view.JSContext.globalParameters',
                                              'preset', GLib.Variant('i', 12))
                self._initialized = True
            elif self._app.get_object_property('view.JSContext.globalParameters', 'quest1Success'):
                return self.step_reward
        except Exception as ex:
            print(ex)

        if time_in_step > 60 and not self._hint1:
            self.show_message(QS('FIZZICS2_HINT2'))
            self._hint1 = True

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_end_no_app

        return step

    # STEP 2
    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('FIZZICS2_SUCCESS'), choices=[('OK', self.go_next_step)])
            self.conf['complete'] = True
            self.available = False
            self.give_item('item.key.hackdex1.1')

        if self._go_next_step:
            self._go_next_step = False
            return self.step_end

        return step

    def step_end(self, step, starting, time_in_step):
        return

    # STEP Abort
    def step_end_no_app(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIZZICS2_ABORT'))

        if time_in_step > 5:
            return

        return step
