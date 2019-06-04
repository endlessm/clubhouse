from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound
from gi.repository import Gio


class BreakSomething(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    CURSOR_NORMAL_SIZE = 24
    CURSOR_HUGE_SIZE = 200

    __available_after_completing_quests__ = ['OSIntro']
    __items_on_completion__ = {'item.key.OperatingSystemApp.1': {}}

    def setup(self):
        self._app = App(self.APP_NAME)
        self.settings = Gio.Settings.new("org.gnome.desktop.interface")

    def step_begin(self):
        self.ask_for_app_launch(self._app)
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        if self._app.get_js_property('flipped'):
            return self.step_givekey

        Sound.play('quests/step-forward')
        confirm_action = self.show_confirm_message('OSAPP')

        flipped_action = self.connect_app_js_props_changes(self._app, ['flipped'])

        self.wait_for_one([confirm_action, flipped_action])

        if self.confirmed_step():
            if not self._app.get_js_property('flipped'):
                self.show_hints_message('FLIP')
                self.wait_for_app_js_props_changed(self._app, ['flipped'])

        return self.step_givekey

    @Quest.with_app_launched(APP_NAME)
    def step_givekey(self):
        item = self.gss.get('item.key.OperatingSystemApp.1')
        # If we already have the key, skip this step.
        if item is not None:
            # If the panel is already unlocked, skip all that
            if item.get('used', False):
                return self.step_unlocked

            # Otherwise prompt player to unlock it
            return self.step_unlock

        Sound.play('quests/step-forward')
        self.wait_confirm('GIVEKEY')

        if self.confirmed_step():
            self.give_item('item.key.OperatingSystemApp.1')
            return self.step_unlock

    @Quest.with_app_launched(APP_NAME)
    def step_unlock(self):
        self.show_hints_message('UNLOCK')
        return self.step_wait_for_unlock

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_unlock(self):
        item = self.gss.get('item.key.OperatingSystemApp.1')
        if item is not None and item.get('used', False):
            return self.step_unlocked

        self.connect_gss_changes().wait()
        # The GSS changes connection may be triggered by any key that has
        # been changed, so we keep trying until we get the result we need.
        return self.step_wait_for_unlock

    @Quest.with_app_launched(APP_NAME)
    def step_unlocked(self):
        Sound.play('quests/step-forward')
        self.show_confirm_message('UNLOCKED')

        while self.settings.get_int('cursor-size') < self.CURSOR_HUGE_SIZE:
            if self.confirmed_step():
                self.show_hints_message('MAKEITLARGE')

            self.wait_for_one([self.get_confirm_action(),
                               self.connect_settings_changes(self.settings, ['cursor-size'])])
            if self.is_cancelled():
                break

        return self.step_success

    @Quest.with_app_launched(APP_NAME)
    def step_success(self):
        Sound.play('quests/step-forward')
        self.wait_confirm('SUCCESS')
        return self.step_saniel

    @Quest.with_app_launched(APP_NAME)
    def step_saniel(self):
        self.wait_confirm('SANIELARRIVES')
        if self.settings.get_int('cursor-size') == self.CURSOR_NORMAL_SIZE:
            return self.step_already_reset

        return self.step_give_reset

    @Quest.with_app_launched(APP_NAME)
    def step_give_reset(self):
        self.show_hints_message('GIVERESET')

        # Set reset button visible
        self.gss.set("app.hack_toolbox.reset_button", {'visible': True})

        Sound.play('quests/reset-given')

        # Check every time the cursor-size is changed, until we get the result we need
        while self.settings.get_int('cursor-size') != self.CURSOR_NORMAL_SIZE:
            self.connect_settings_changes(self.settings, ['cursor-size']).wait()
            if self.is_cancelled():
                break

        return self.step_reset

    @Quest.with_app_launched(APP_NAME)
    def step_reset(self):
        Sound.play('quests/step-forward')
        self.wait_confirm('RESET')

        return self.step_reward

    @Quest.with_app_launched(APP_NAME)
    def step_already_reset(self):
        # Set reset button visible
        self.gss.set("app.hack_toolbox.reset_button", {'visible': True})

        Sound.play('quests/reset-given')
        self.wait_confirm('ALREADYRESET')

        return self.step_reward

    def step_reward(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')

        self.wait_confirm('WRAPUP')
        self.stop()
