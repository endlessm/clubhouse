from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsCode1(Quest):

    APP_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Code 1', 'ada')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            Desktop.focus_app(self.APP_NAME)
            self.wait_for_app_launch(self._app)
            self.pause(2)

        return self.step_flip

    def step_abort(self):
        Sound.play('quests/quest-aborted')
        self.show_message('ABORT')

        self.pause(5)
        self.stop()

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_flip(self):
        if self._app.get_js_property('flipped'):
            return self.step_unlock

        Sound.play('quests/step-forward')
        self.show_hints_message('FLIP')
        while not self._app.get_js_property('flipped') and not self.is_cancelled():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        return self.step_unlock

    def _is_panel_unlocked(self):
        item = self.gss.get('item.key.fizzics.2')
        return item is not None and item.get('used', False)

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_unlock(self):
        if self._is_panel_unlocked():
            return self.step_explanation1

        Sound.play('quests/step-forward')
        self.show_hints_message('UNLOCK')
        while not self._is_panel_unlocked() and not self.is_cancelled():
            self.connect_gss_changes().wait()

        return self.step_explanation1

    def _has_radius_changed(self, prev_radius):
        return self._app.get_js_property('radius_0', prev_radius) != prev_radius

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_explanation1(self):
        Sound.play('quests/step-forward')
        self.show_hints_message('EXPLANATION1')

        prev_radius = self._app.get_js_property('radius_0', 0)
        while not self._has_radius_changed(prev_radius) and not self.is_cancelled():
            # @todo: Connect to app property changes instead of
            # polling. This needs a fix in Clippy. See
            # https://phabricator.endlessm.com/T25359
            self.pause(0.5)

        return self.step_explanation2

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_explanation2(self):
        Sound.play('quests/step-forward')
        self.show_hints_message('EXPLANATION2')

        # Add a delay, otherwise this would get triggered by clicking on the + multiple times
        self.pause(4)

        # @todo: this quest doesn't check if the radious was chenged
        # with code, as the EXPLANATION2 asks the user to do.
        prev_radius = self._app.get_js_property('radius_0', 0)
        while not self._has_radius_changed(prev_radius) and not self.is_cancelled():
            # @todo: Connect to app property changes instead of
            # polling. This needs a fix in Clippy. See
            # https://phabricator.endlessm.com/T25359
            self.pause(0.5)

        return self.step_end

    def step_end(self):
        Sound.play('quests/step-forward')
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_message('END', choices=[('Bye', self.stop())])
