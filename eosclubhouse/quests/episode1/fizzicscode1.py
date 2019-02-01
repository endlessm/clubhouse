from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsCode1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Code 1', 'ada')
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._prev_radius = 0

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                self.show_hints_message('LAUNCH')
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
                return self.step_unlock
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        # Step dialog at the end so we can move forward without flashing dialogs
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('FLIP')

    def step_unlock(self, time_in_step):
        # Wait until they unlock the panel
        item = self.gss.get('item.key.fizzics.2')
        if item is not None and item.get('used', False):
            return self.step_explanation1
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        # Step dialog at the end so we can move forward without flashing dialogs
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('UNLOCK')

    def step_explanation1(self, time_in_step):
        if time_in_step == 0:
            self._prev_radius = self._app.get_js_property('radius_0', 0)
            Sound.play('quests/step-forward')
            self.show_hints_message('EXPLANATION1')

        if self._app.get_js_property('radius_0', self._prev_radius) != self._prev_radius:
            return self.step_explanation2
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_explanation2(self, time_in_step):
        if time_in_step == 0:
            self._prev_radius = -10000
            Sound.play('quests/step-forward')
            self.show_hints_message('EXPLANATION2')

        # Add a delay, otherwise this would get triggered by clicking on the + multiple times
        if time_in_step < 4:
            return
        if self._prev_radius == -10000:
            self._prev_radius = self._app.get_js_property('radius_0', 0)

        if self._app.get_js_property('radius_0', self._prev_radius) != self._prev_radius:
            return self.step_end
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_end(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_message('END', choices=[('Bye', self._confirm_step)])
        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
