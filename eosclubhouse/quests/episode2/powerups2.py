from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class PowerUps2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('PowerUps2', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLAIN')
        return self.step_code

    def step_abort(self):
        Sound.play('quests/quest-aborted')
        self.show_message('ABORT')

        self.pause(5)
        self.stop()

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_code(self):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        self.show_hints_message('CODE')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_code2

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_code2(self):
        self.show_hints_message('CODE2')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_spawn

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_spawn(self):
        self.show_hints_message('SPAWN')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_play

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_play(self):
        self.show_hints_message('PLAY')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_success

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_success(self):
        self.show_hints_message('SUCCESS')

        while not (self.debug_skip() or self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['DummyProperty'])

        return self.step_end

    def step_end(self):
        self.give_item('item.stealth.4')
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
