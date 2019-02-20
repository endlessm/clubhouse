from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Investigation(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Investigation', 'riley')
        self._app = App(self.APP_NAME)
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("MakerIntro"):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('FLIP')
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_unlock

        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_unlock(self):
        self.show_hints_message('UNLOCK')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_stop

    @Quest.with_app_launched(APP_NAME)
    def step_stop(self):
        self.show_hints_message('STOP')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_end

    def step_end(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
