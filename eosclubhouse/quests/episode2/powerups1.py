from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class PowerUps1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('PowerUps1', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLAIN')
        return self.step_codepowerup

    @Quest.with_app_launched(APP_NAME)
    def step_codepowerup(self):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        self.show_hints_message('CODEPOWERUP')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_spawn

    @Quest.with_app_launched(APP_NAME)
    def step_spawn(self):
        self.show_hints_message('SPAWN')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_success

    @Quest.with_app_launched(APP_NAME)
    def step_success(self):
        self.show_hints_message('SUCCESS')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_end

    def step_end(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
