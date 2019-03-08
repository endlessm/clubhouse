from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyB2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyB2', 'saniel')
        self._app = LightSpeed()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self._app.set_level(7)
        self.show_hints_message('EXPLAIN')
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_code(self):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        self._app.reveal_topic('spawnEnemy')

        self.show_hints_message('CODE')

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_play(self):
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
            return self.step_success

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
    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.give_item('item.stealth.4')
        return self.step_end

    def step_end(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
