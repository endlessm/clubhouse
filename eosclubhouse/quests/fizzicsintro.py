from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada', QS('FIZZICSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICSINTRO_LAUNCH'))
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICSINTRO_EXPLANATION'))

        try:
            if self._app.get_object_property('view.JSContext.globalParameters',
                                             'currentLevel') == 2:
                return self.step_success
        except Exception as ex:
            print(ex)
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_SUCCESS'))
        if self.confirmed_step():
            return self.step_ricky

    def step_ricky(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/riley-intro')
            self.show_question(QS('FIZZICSINTRO_RICKY'), character_id='ricky')
        if self.confirmed_step():
            return self.step_intro

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_INTRO'))
        if self.confirmed_step():
            return self.step_key

    def step_key(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.give_item('item.key.fizzics.1')
            self.show_question(QS('FIZZICSINTRO_KEY'))
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICSINTRO_ABORT'))

        if time_in_step > 5:
            self.stop()
