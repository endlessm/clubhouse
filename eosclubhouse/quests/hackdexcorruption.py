import time

from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App
from gi.repository import GObject, GLib

class HackdexCorruption(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'

    def __init__(self):
        super().__init__('Hackdex Corruption', 'archivist', QS('HACKDEX1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self._go_next_step = False
        self._hint_key = False
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

    def get_dictionary_from_state(self, key):
        try:
            data = self.gss.get(key)
        except GLib.Error as e:
            pass
        except Exception as e:
            logger.debug(e.message)
        else:
            return data
        return None


    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if (self.is_named_quest_complete("BreakSomething")):
            self.available = True

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            variant = GLib.Variant('a{ss}', {'state': 'corrupted', 'color': ''})
            self.gss.set('app.com_endlessm_Hackdex_chapter_one.corruption', variant)
            self.show_message(QS('HACKDEX1_LAUNCH'))

        if time_in_step < 3:
            return step

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

        return step

    def step_delay1(self, step, starting, time_in_step):
        if time_in_step > 3:
            return self.step_explanation
        return step

    def step_explanation(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('HACKDEX1_GOAL'))

        # Check unlock level 1
        if self.is_item_used('item.key.hackdex1.1'):
            return self.step_check_goal

        if (time_in_step > 20 and not self._hint_key):
            self._msg = QS('HACKDEX1_NEED_KEY')
            self.show_message(self._msg)
            self._hint_key = True

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        return step

    def step_check_goal(self, step, starting, time_in_step):
        if starting:
            self.show_message(QS('HACKDEX1_UNLOCKED'))

        # Check for color change
        data = self.get_dictionary_from_state('app.com_endlessm_Hackdex_chapter_one.corruption')
        if data is None:
            return self.step_abort

        if data['state'] == 'fixed' or self.debug_skip():
            return self.step_delay2

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        return step

    def step_delay2(self, step, starting, time_in_step):
        if time_in_step > 3:
            return self.step_success
        return step

    def step_success(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('HACKDEX1_SUCCESS'), choices=[('OK', self.go_next_step)])
            self.give_item('item.key.fizzics.2')

        if self._go_next_step:
            self._go_next_step = False
            return self.step_ricky

        return step

    def step_ricky(self, step, starting, time_in_step):
        if starting:
            self.show_question(QS('HACKDEX1_RICKY'), choices=[('OK', self.go_next_step)],
                               character_id='ricky')
            self.give_item('item.mysterious_object')
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
            self.show_message(QS('HACKDEX1_ABORT'))

        if time_in_step > 5:
            return

        return step
