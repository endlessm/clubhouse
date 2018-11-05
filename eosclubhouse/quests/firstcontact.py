import time

from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class FirstContact(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.HackUnlock'

    # This quest starts already in the first step. There's no prompting.
    def __init__(self):
        super().__init__('First Contact', 'ada', '')
        self._app = App(self.TARGET_APP_DBUS_NAME)

        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = False
        self.skippable = True

        self._go_next_step = False

    def start(self):
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

    def get_hackunlock_mode(self):
        mode = 0

        try:
            mode = self._app.get_object_property('view.JSContext.globalParameters', 'mode')
        except Exception as e:
            print(e)

        return mode

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIRSTCONTACT_WELCOME'))

        if time_in_step < 3:
            return step

        if self.get_hackunlock_mode() >= 1 or self.debug_skip():
            return self.step_dohack

        return step

    # STEP 1
    def step_dohack(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIRSTCONTACT_GOAL'))

        if self.get_hackunlock_mode() >= 2 or self.debug_skip():
            return self.step_flipback

        return step

    def step_flipback(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('FIRSTCONTACT_FLIPBACK'))

        if self.get_hackunlock_mode() >= 4 or self.debug_skip():
            return self.step_reward

        return step

    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('FIRSTCONTACT_REWARD'), choices=[('OK', self.go_next_step)])
            self.conf['complete'] = True
            self.available = False

        if self._go_next_step:
            self._go_next_step = False
            return self.step_end

        return step

    def step_end(self, step, starting, time_in_step):
        return
