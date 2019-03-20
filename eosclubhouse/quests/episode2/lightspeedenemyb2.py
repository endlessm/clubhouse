from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyB2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyB2', 'saniel')
        self._app = LightSpeed()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)

        self._app.set_level(7)
        self.show_hints_message('EXPLAIN')
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_code(self):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_abouttoplay

        self._app.reveal_topic('spawnEnemy')

        self.show_hints_message('CODE')

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_abouttoplay(self):
        if not self._app.get_js_property('playing'):
            self.show_hints_message('ABOUTTOPLAY')
            self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_playtest

    @Quest.with_app_launched(APP_NAME)
    def step_playtest(self):
        self.show_hints_message('PLAYING')
        self.pause(12)

        enemy0_count = self._app.get_js_property('enemyType0SpawnedCount', -1)
        enemy1_count = self._app.get_js_property('enemyType1SpawnedCount', -1)
        enemy2_count = self._app.get_js_property('enemyType2SpawnedCount', -1)
        zero_count = 0
        if (enemy0_count == 0):
            zero_count += 1
        if (enemy1_count == 0):
            zero_count += 1
        if (enemy2_count == 0):
            zero_count += 1

        if zero_count <= 1 or self.debug_skip():
            self.show_hints_message('FINISHLEVEL')
            return self.step_finishlevel

        if enemy0_count == 0 and enemy1_count == 0 and enemy2_count == 0:
            self.show_hints_message('NOENEMIES')
            return self.step_wait_for_flip

        self.show_hints_message('SOMENEMIES')
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_finishlevel(self):
        if self._app.get_js_property('success'):
            return self.step_success
        if not self._app.get_js_property('playing'):
            return self.step_abouttoplay
        self.wait_for_app_js_props_changed(self._app, ['playing', 'success'])
        return self.step_finishlevel

    @Quest.with_app_launched(APP_NAME)
    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.give_item('item.stealth.4', consume_after_use=True)
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
