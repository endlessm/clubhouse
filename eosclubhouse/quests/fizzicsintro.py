from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada', QS('FIZZICSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICSINTRO_LAUNCH'))

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_explanation

    # STEP 1
    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_EXPLANATION'))
        if self.confirmed_step():
            return self.step_ricky

    def step_ricky(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_RICKY'), character_id='ricky')
        if self.confirmed_step():
            return self.step_intro

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question(QS('FIZZICSINTRO_INTRO'))
        if self.confirmed_step():
            self.stop()
