import time

from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, GameStateService


class HackdexCorruption(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'

    def __init__(self):
        super().__init__('Hackdex Corruption', 'archivist', QS('HACKDEX1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._game_state_service = GameStateService()
        self._game_state_service.connect('changed', self.update_availability)
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

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if (self.is_named_quest_complete("BreakSomething")):
            self.available = True

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('HACKDEX1_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

        return step

    # STEP 1
    def step_explanation(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('HACKDEX1_GOAL'))

        # TODO: Check quest completion with invisible ink change
        if self.debug_skip():
            return self.step_success

        return step

    def step_success(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('HACKDEX1_SUCCESS'))
            self.give_item('item.key.fizzics.2')

        if time_in_step > 5:
            return self.step_ricky

        return step

    def step_ricky(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('HACKDEX1_RICKY'))
            self.give_item('item.mysterious_object')
            self.conf['complete'] = True
            self.available = False

        if time_in_step > 5:
            return

        return step
