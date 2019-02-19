from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class BreakingIn(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('BreakingIn', 'riley')
        self._app = App(self.APP_NAME)
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("MakeDevice"):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLAIN')

        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        return self.step_flipped

    def level2_is_unlocked(self):
        # @todo: Check if the needed panel is unlocked
        return self.debug_skip()

    @Quest.with_app_launched(APP_NAME)
    def step_flipped(self):
        self.show_hints_message('FLIPPED')

        while not (self.level2_is_unlocked() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_unlocked

    @Quest.with_app_launched(APP_NAME)
    def step_unlocked(self):
        self.wait_confirm('UNLOCKED')
        return self.step_archivist

    def step_archivist(self):
        self.show_confirm_message('ARCHIVIST', confirm_label='End of Episode 2').wait()
        if not self.confirmed_step():
            return

        Sound.play('quests/quest-complete')
        self.conf['complete'] = True
        self.available = False

        self.stop()
