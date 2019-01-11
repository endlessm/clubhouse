from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsCode2(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Code 2', 'riley')
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("FizzicsCode1"):
            self.available = True

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                self.show_hints_message('FIZZICSCODE2_LAUNCH')
                Desktop.focus_app(self.TARGET_APP_DBUS_NAME)
            else:
                return self.step_flip

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_flip

    def step_flip(self, time_in_step):
        try:
            # Check for flipping the app
            if self._app.get_js_property('flipped'):
                return self.step_explanation
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        # Step dialog at the end so we can move forward without flashing dialogs
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('FIZZICSCODE2_FLIP')

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('FIZZICSCODE2_EXPLANATION')

        try:
            if self._app.get_js_property('gravity_0') < 0:
                return self.step_end
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_end(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.conf['complete'] = True
            self.available = False
            self.complete_current_episode()
            Sound.play('quests/quest-complete')
            self.show_message('FIZZICSCODE2_END', choices=[('Bye', self._confirm_step)])
        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('FIZZICSCODE2_ABORT')

        if time_in_step > 5:
            self.stop()
