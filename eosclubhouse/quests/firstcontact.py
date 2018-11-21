from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class FirstContact(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.HackUnlock'

    # This quest starts already in the first step. There's no prompting.
    def __init__(self):
        super().__init__('First Contact', 'ada', '')
        self._app = None
        self._hint1 = False
        self._hint2 = False

        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = False
        self.skippable = True

    def get_hackunlock_mode(self):
        if self._app is None:
            self._app = App(self.TARGET_APP_DBUS_NAME)

        mode = 0

        try:
            mode = self._app.get_object_property('view.JSContext.globalParameters', 'mode')
        except Exception as e:
            print(e)

        return mode

    # Waiting for player to flip app
    def step_first(self, time_in_step):
        # Starting out without any dialog

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or time_in_step < 3:
            return

        if self.get_hackunlock_mode() >= 1:
            self._hint1 = False
            self._hint2 = False
            return self.step_dohack

        if time_in_step >= 10 and not self._hint1:
            self.show_message(QS('FIRSTCONTACT_WELCOME_HINT1'))
            self._hint1 = True
        elif time_in_step >= 20 and not self._hint2:
            self.show_message(QS('FIRSTCONTACT_WELCOME_HINT2'))
            self._hint2 = True

    # App has been flipped
    def step_dohack(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIRSTCONTACT_GOAL'))

        if self.get_hackunlock_mode() >= 2:
            self._hint1 = False
            self._hint2 = False
            return self.step_flipback

        if time_in_step > 20 and not self._hint1:
            self._hint1 = True
            self.show_message(QS('FIRSTCONTACT_GOAL_HINT1'))
        if time_in_step > 40 and not self._hint2:
            self._hint2 = True
            self.show_message(QS('FIRSTCONTACT_GOAL_HINT2'))

    # Hack is done. Waiting for player to flip back
    def step_flipback(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIRSTCONTACT_FLIPBACK'))

        if self.get_hackunlock_mode() >= 4 or self.debug_skip():
            return self.step_reward

        if time_in_step > 8 and not self._hint1:
            self._hint1 = True
            self.show_message(QS('FIRSTCONTACT_FLIPBACK_HINT1'))

    def step_reward(self, time_in_step):
        self.conf['complete'] = True
        self.available = False
        self.stop()
