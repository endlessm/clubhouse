from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyC2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyC2', 'riley')
        self._app = LightSpeed()

    def step_begin(self):
        self._app.reveal_topic('spawn')

        self.ask_for_app_launch(self._app, pause_after_launch=2)

        self._app.set_level(8)
        self.show_hints_message('EXPLAIN')
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        code_msg_id = 'CODE'

        if (not self._app.get_js_property('flipped') or self.debug_skip()) and \
           self._app.get_js_property('playing'):
            enemy_count = self._app.get_js_property('enemyType1SpawnedCount', 0)

            if enemy_count == 0:
                code_msg_id = 'ADD_ENEMY_CODE'

            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code, code_msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_code(self, msg_id):
        self._app.reveal_topic('updateBeam')
        self.show_hints_message(msg_id)

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
        self.pause(10)

        min_y = self._app.get_js_property('enemyType3MinY', +10000)
        max_y = self._app.get_js_property('enemyType3MaxY', -10000)
        if min_y > max_y:
            self.show_hints_message('NOENEMIES')
            return self.step_wait_for_flip
        if min_y == max_y:
            self.show_hints_message('NOTMOVING')
            return self.step_wait_for_flip
        return self.step_moving

    @Quest.with_app_launched(APP_NAME)
    def step_moving(self):
        self.show_hints_message('MOVING')
        if self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing', 'success'])

        if self._app.get_js_property('success') or self.debug_skip():
            return self.step_success

        self.show_hints_message('FAILED')

        if not self._app.get_js_property('flipped') and not self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing', 'flipped'])
        if self._app.get_js_property('flipped'):
            return self.step_code, 'CODE'
        # playing
        return self.step_playtest

    def step_success(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()
        self.stop()
