from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound

# @todo: This quest only changes a few lines from the LightSpeedEnemyA2 quest, so we should make
# sure that we use a common base but only after both quests' development is finished (otherwise,
# optimizing ATM may end up making things more complicated).


class LightSpeedEnemyA4(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'
    SCREEN_HEIGHT = 1004

    def __init__(self):
        super().__init__('LightSpeedEnemyA4', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        self._app.reveal_topic('spawnEnemy')
        self._app.reveal_topic('updateSpinner')

        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLANATION')
        self._app.set_level(5)
        return self.step_wait_for_flip, 'CODE'

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self, code_msg_id):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code, code_msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_code(self, code_msg_id):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        self.show_hints_message(code_msg_id)

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code, code_msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_play(self):
        self.show_hints_message('PLAYING')
        self.pause(10)

        if self.debug_skip():
            return self.step_success

        min_y = self._app.get_js_property('enemyType1MinY', +10000)
        max_y = self._app.get_js_property('enemyType1MaxY', -10000)

        if min_y == max_y:
            self.show_hints_message('NOTMOVING')
            return self.step_wait_for_flip, 'CODE'
        if min_y < -20:
            self.show_hints_message('GOINGUNDER')
            return self.step_wait_for_flip, 'CODE'
        if min_y > 10:
            self.show_hints_message('NOTLOWENOUGH')
            return self.step_wait_for_flip, 'CODE'
        if max_y > self.SCREEN_HEIGHT + 20:
            self.show_hints_message('GOINGOVER')
            return self.step_wait_for_flip, 'CODE2'
        if max_y < self.SCREEN_HEIGHT - 10:
            self.show_hints_message('NOTHIGHENOUGH')
            return self.step_wait_for_flip, 'CODE2'
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.give_item('item.stealth.2', consume_after_use=True)
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()
        self.stop()
