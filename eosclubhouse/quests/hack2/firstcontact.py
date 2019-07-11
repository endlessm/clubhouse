from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Desktop


class FirstContact(Quest):

    APP_NAME = 'com.endlessm.HackUnlock'

    __tags__ = ['mission:ada']

    # This quest starts already in the first step. There's no prompting.
    __proposal_message_id__ = ''

    def setup(self):
        self._app = App(self.APP_NAME)

        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = False
        self.skippable = True

    def _is_app_flipped(self):
        if not self._app.is_running():
            return False
        return self._app.get_js_property('mode', default_value=0) >= 1

    def _is_app_hacked(self):
        if not self._app.is_running():
            return False
        return self._app.get_js_property('mode', default_value=0) >= 2

    def _is_app_flipped_back(self):
        if not self._app.is_running():
            return False
        return self._app.get_js_property('mode', default_value=0) >= 4

    def step_reward(self):
        Desktop.personalize_desktop(True)
        self.complete = True
        self.available = False
        self.stop()

    def step_begin(self):
        Desktop.set_hack_mode(True)

        self._app.launch()

        self.wait_for_app_launch(self._app, pause_after_launch=3)

        if self._is_app_flipped():
            return self.step_wait_for_hack

        return self.step_wait_and_pulse

    @Quest.with_app_launched(APP_NAME)
    def step_wait_and_pulse(self):
        self._app.pulse_flip_to_hack_button(True)

        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        for hint_msg_id in ['WELCOME', 'WELCOME_HINT1']:
            if self._is_app_flipped() or self.is_cancelled():
                break
            self.wait_for_app_js_props_changed(self._app, ['mode'], timeout=10)
            if not self._is_app_flipped():
                self.show_message(hint_msg_id)

        while not self._is_app_flipped() and not self.is_cancelled():
            self.wait_for_app_js_props_changed(self._app, ['mode'])

        self._app.pulse_flip_to_hack_button(False)
        return self.step_wait_for_hack

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_hack(self):
        self.show_message('GOAL')

        for hint_msg_id in ['GOAL_HINT1', 'GOAL_HINT2']:
            if self._is_app_hacked() or self.is_cancelled():
                break
            self.wait_for_app_js_props_changed(self._app, ['mode'], timeout=20)
            if not self._is_app_hacked():
                self.show_message(hint_msg_id)

        while not self._is_app_hacked() and not self.is_cancelled():
            self.wait_for_app_js_props_changed(self._app, ['mode'])

        self._app.pulse_flip_to_hack_button(True)
        return self.step_wait_for_flipback

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flipback(self):
        self.show_message('FLIPBACK')

        if not self._is_app_flipped_back():
            self.wait_for_app_js_props_changed(self._app, ['mode'], timeout=8)
            if not self._is_app_flipped_back():
                self.show_message('FLIPBACK_HINT1')

        while not self._is_app_flipped_back() and not self.is_cancelled():
            self.wait_for_app_js_props_changed(self._app, ['mode'])

        self._app.pulse_flip_to_hack_button(False)
        return self.step_reward

    def abort(self):
        Desktop.set_hack_mode(False)
        super().abort()
