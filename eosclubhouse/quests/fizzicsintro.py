import time

from eosclubhouse.libquest import Quest
from eosclubhouse.desktop import App


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackyballs'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada',
                         "I would like to show you what tool I use for my research.")
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._hintCount = False
        self._initialized = False
        self._msg = ""

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

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message("Starting the quest.")

        if (time_in_step > 2):
            return self.step_reward

        return step

    # STEP 1
    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_message("Done!")
            self.conf['complete'] = True

        if time_in_step > 2:
            return

        return step

