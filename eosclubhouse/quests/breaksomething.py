from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class BreakSomething(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Break Something', 'ricky', QS('BREAK_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("OSIntro"):
            self.available = True

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

    # STEP 1
    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_OSAPP'))

        # TODO: Wait for flip to hack
        if self.debug_skip():
            return self.step_unlock

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_unlock(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_UNLOCK'))

        item = self.gss.get('item.key.OperatingSystemApp.1')
        if item is not None and item.get('used', False):
            return self.step_unlocked
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_unlocked(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_UNLOCKED'))

        # TODO: Wait for goal to be met (large cursor)
        if self.debug_skip():
            return self.step_success
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_SUCCESS'))
        if self.confirmed_step():
            return self.step_reset

    def step_reset(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_ARCHIVISTARRIVES'), character_id='archivist')

        # TODO: Wait for goal to be met (reset button)
        if self.debug_skip():
            return self.step_reward

    def step_reward(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_WRAPUP'), character_id='archivist')
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_ABORT'))

        if time_in_step > 5:
            self.stop()
