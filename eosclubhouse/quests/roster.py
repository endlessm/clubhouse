from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class Roster(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'

    def __init__(self):
        super().__init__('Roster', 'ada', QS('ROSTER_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('ROSTER_LAUNCH'))
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('ROSTER_EXPLANATION'))

        if time_in_step < 5:
            return

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_closed

        if time_in_step > 60 * 2:
            return self.step_timeout

    def step_closed(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('ROSTER_CLOSED'))
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()

    def step_timeout(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('ROSTER_TIMEOUT'))
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()
