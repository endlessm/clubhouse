from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyA1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    __available_after_completing_quests__ = ['LightSpeedFix2', 'StealthDevice']

    def __init__(self):
        super().__init__('LightSpeedEnemyA1', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_newlevel

    @Quest.with_app_launched(APP_NAME)
    def step_newlevel(self):
        self.show_hints_message('NEWLEVEL')
        self._app.set_level(5)
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_code(self):
        self._app.reveal_topic('spawnEnemy')
        self.show_hints_message('CHANGEENEMY')

        if self._app.get_js_property('flipped'):
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_abouttoplay

    @Quest.with_app_launched(APP_NAME)
    def step_abouttoplay(self):
        if not self._app.get_js_property('playing'):
            self.show_hints_message('ABOUTTOPLAY')
            self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_playtest

    @Quest.with_app_launched(APP_NAME)
    def step_playtest(self):
        self.show_hints_message('PLAYTEST')
        if self._app.get_js_property('paused'):
            self.wait_for_app_js_props_changed(self._app, ['paused'])
        self.pause(5)

        enemy0_count = self._app.get_js_property('enemyType0SpawnedCount')
        enemy1_count = self._app.get_js_property('enemyType1SpawnedCount')
        if (enemy0_count == 0 and enemy1_count == 0):
            self.show_hints_message('NOENEMIES')
            return self.step_wait_for_flip
        if (enemy1_count == 0):
            self.show_hints_message('NOSPINNERS')
            return self.step_wait_for_flip

        return self.step_success

    def step_success(self):
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        self.stop()
