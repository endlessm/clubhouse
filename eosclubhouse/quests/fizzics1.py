import time

from gi.repository import GLib
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class Fizzics1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackyballs'

    def __init__(self):
        super().__init__('Fizzics 1', 'ricky', QS('FIZZICS1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._hintCount = False
        self._initialized = False
        self._msg = ""
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
        if (self.is_named_quest_complete("FizzicsIntro")):
            self.available = True

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIZZICS1_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_goal

        if (time_in_step > 20 and not self._hint0):
            self.show_message(QS('FIZZICS1_LAUNCHHINT'))
            self._hint0 = True

        return step

    # STEP 1
    def step_goal(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIZZICS1_GOAL'))

        if time_in_step < 3:
            return step

        try:
            if not self._initialized:
                self._app.set_object_property('view.JSContext.globalParameters',
                                              'preset',
                                              GLib.Variant('i', 11))
                self._initialized = True
        except Exception as ex:
            print(ex)

        if time_in_step > 20:
            return self.step_wait_score

        return step

    def step_wait_score(self, step, starting, time_in_step):
        if starting:
            self._msg = QS('FIZZICS1_EXPLANATION')
            self.show_message(self._msg)
            self.give_item('item.key.fizzics.1')

        try:
            if self._app.get_object_property('view.JSContext.globalParameters',
                                             'quest0Success'):
                return self.step_success

            type1BallCount = self._app.get_object_property('view.JSContext.globalParameters',
                                                           'type1BallCount')
            if (time_in_step > 5 and type1BallCount < 20 and not self._hintCount):
                self.show_message(QS('FIZZICS1_NOTENOUGH'))
                self._hintCount = True
            elif (type1BallCount >= 20 and self._hintCount):
                self.show_message(self._msg)
                self._hintCount = False
            elif (time_in_step > 60 and not self._hint1):
                self._msg = QS('FIZZICS1_HINT')
                self.show_message(self._msg)
                self._hint1 = True
        except Exception as ex:
            print(ex)

        if self.debug_skip():
            return self.step_success

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_end_no_app

        return step

    # STEP 2
    def step_success(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('FIZZICS1_SUCCESS'), choices=[('OK', self.go_next_step)])

        if self._go_next_step:
            self._go_next_step = False
            return self.step_prereward

        return step

    def step_prereward(self, step, starting, time_in_step):
        if starting:
            if (self.is_named_quest_complete("OSIntro")):
                msg = 'FIZZICS1_KEY_ALREADY_OS'
            else:
                msg = 'FIZZICS1_KEY_NO_OS'
            self.show_question(QS(msg), choices=[('OK', self.go_next_step)])

        if self._go_next_step:
            self._go_next_step = False
            return self.step_reward

        return step

    # STEP 4
    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.give_item('item.key.OperatingSystemApp.1')
            self.show_question(QS('FIZZICS1_GIVE_KEY'), choices=[('OK', self.go_next_step)])
            self.conf['complete'] = True
            self.available = False

        if self._go_next_step:
            self._go_next_step = False
            return self.step_end

        return step

    def step_end(self, step, starting, time_in_step):
        return

    # STEP Abort
    def step_end_no_app(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIZZICS1_ABORT'))

        if time_in_step > 5:
            return

        return step
