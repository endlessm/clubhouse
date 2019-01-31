from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class FirstContact(Quest):

    APP_NAME = 'com.endlessm.HackUnlock'

    # This quest starts already in the first step. There's no prompting.
    def __init__(self):
        super().__init__('First Contact', 'ada', '')
        self._app = App(self.APP_NAME)

        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = False
        self.skippable = True

    def _is_app_flipped(self):
        return self._app.get_js_property('mode', default_value=0) >= 1

    def _is_app_hacked(self):
        return self._app.get_js_property('mode', default_value=0) >= 2

    def _is_app_flipped_back(self):
        return self._app.get_js_property('mode', default_value=0) >= 4

    def step_reward(self):
        self.conf['complete'] = True
        self.available = False
        self.stop()

    def step_begin(self):
        self.wait_for_app_launch(self._app)
        self.pause(3)
        return self.step_one

    @Quest.with_app_launched(APP_NAME, otherwise=step_reward)
    def step_one(self):
        if self._is_app_flipped():
            return self.step_dohack

        self.show_hints_message('WELCOME')
        while not self._is_app_flipped():
            self.wait_for_app_js_props_changed(self._app, ['mode'])

        return self.step_dohack

    @Quest.with_app_launched(APP_NAME, otherwise=step_reward)
    def step_dohack(self):
        if self._is_app_hacked():
            return self.step_flipback

        self.show_hints_message('GOAL')
        while not self._is_app_hacked():
            self.wait_for_app_js_props_changed(self._app, ['mode'])

        return self.step_flipback

    @Quest.with_app_launched(APP_NAME, otherwise=step_reward)
    def step_flipback(self):
        if self._is_app_flipped_back():
            return self.step_reward

        self.show_hints_message('FLIPBACK')
        while not self._is_app_flipped_back():
            self.wait_for_app_js_props_changed(self._app, ['mode'])

        return self.step_reward
