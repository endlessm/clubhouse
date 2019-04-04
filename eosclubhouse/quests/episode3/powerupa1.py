from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class PowerUpA1(Quest):

    __available_after_completing_quests__ = ['ApplyFob1']

    def __init__(self):
        super().__init__('PowerUpA1', 'saniel')
        self._app = LightSpeed()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)

        # @todo: set correct level
        self._app.set_level(8)
        return self.step_flip

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_flip(self):
        if self._app.get_js_property('flipped'):
            return self.step_code

        self.show_hints_message('EXPLAIN')
        while ((not self._app.get_js_property('flipped') or self.debug_skip()) and not
               self.is_cancelled()):
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        return self.step_code

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_code(self):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        self.show_hints_message('CODE')
        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_play(self):
        self.wait_confirm('ABOUTTOPLAY')
        self.wait_confirm('PLAYTEST')
        self.wait_confirm('NOPOWERUPS')
        self.wait_confirm('FINISHLEVEL')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
