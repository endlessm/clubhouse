from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyC1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyC1', 'riley')
        self._app = LightSpeed()
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("LightSpeedEnemyA4"):
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

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_spawn

    @Quest.with_app_launched(APP_NAME)
    def step_spawn(self):
        self.show_hints_message('SPAWN')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_success

    def step_success(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        self.stop()
