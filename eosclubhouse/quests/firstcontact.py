from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class FirstContact(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.HackUnlock'

    # This quest starts already in the first step. There's no prompting.
    def __init__(self):
        super().__init__('First Contact', 'ada', '')
        self._app = None
        self._hint = False

        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = True
        self.skippable = False

    def get_hackunlock_mode(self):
        if self._app is None:
            self._app = App(self.TARGET_APP_DBUS_NAME)

        mode = 0

        try:
            mode = self._app.get_object_property('view.JSContext.globalParameters', 'mode')
        except Exception as e:
            print(e)

        return mode

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIRSTCONTACT_WELCOME'))

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or time_in_step < 3:
            return

        if self.get_hackunlock_mode() >= 1:
            return self.step_dohack

    # STEP 1
    def step_dohack(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIRSTCONTACT_GOAL'))

        if self.get_hackunlock_mode() >= 2 or self.debug_skip():
            return self.step_flipback
        if time_in_step > 30 and not self._hint:
            self._hint = True
            self.show_message(QS('FIRSTCONTACT_HINT'))

    def step_flipback(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIRSTCONTACT_FLIPBACK'))

        if self.get_hackunlock_mode() >= 4 or self.debug_skip():
            return self.step_reward

    def step_reward(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIRSTCONTACT_REWARD'))
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()
