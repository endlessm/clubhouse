from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class OSIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('OS Intro', 'ada', QS('OSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('OSINTRO_LAUNCH'))
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_EXPLANATION'))

        if self.confirmed_step():
            return self.step_archivist
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_archivist(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_ARCHIVIST'), character_id='archivist')

        if self.confirmed_step():
            return self.step_intro
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_INTRO'))

        if self.confirmed_step():
            return self.step_archivist2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_archivist2(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_ARCHIVIST2'), character_id='archivist')

        if self.confirmed_step():
            return self.step_wrapup
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_wrapup(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_WRAPUP'))
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('OSINTRO_ABORT'))

        if time_in_step > 5:
            self.stop()