from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyA2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyA2', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        self._app.reveal_topic('spawnEnemy')

        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLANATION')
        self._app.set_level(5)
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        code_msg_id = 'CODE'

        if not self._app.get_js_property('flipped') or self.debug_skip():
            enemy_count = self._app.get_js_property('enemyType1SpawnedCount', 0)

            if enemy_count == 0:
                code_msg_id = 'ADD_ENEMY_CODE'

            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code, code_msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_code(self, msg_id):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        self._app.reveal_topic('updateSpinner')

        self.show_hints_message(msg_id)

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code, msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_play(self):
        self.show_hints_message('PLAYING')
        self.pause(10)

        if self.debug_skip():
            return self.step_success

        enemy_count = self._app.get_js_property('enemyType1SpawnedCount', 0)
        min_y = self._app.get_js_property('enemyType1MinY', +10000)
        max_y = self._app.get_js_property('enemyType1MaxY', -10000)

        if enemy_count == 0 or min_y > max_y:
            self.show_hints_message('NOENEMIES')
            return self.step_wait_for_flip
        if min_y == max_y:
            self.show_hints_message('NOTMOVING')
            return self.step_wait_for_flip
        if min_y > 0:
            self.show_hints_message('GOINGUP')
            return self.step_wait_for_flip
        return self.step_success

    def step_success(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()
        self.stop()
