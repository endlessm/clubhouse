from eosclubhouse import logger
from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound

# @todo: This quest only changes a few lines from the LightSpeedEnemyA2 quest, so we should make
# sure that we use a common base but only after both quests' development is finished (otherwise,
# optimizing ATM may end up making things more complicated).


class LightSpeedEnemyA3(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyA3', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        self._app.reveal_topic('spawnEnemy')

        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            # Waiting that long because anything less would cause code not to be set correctly,
            # maybe because Lightspeed was loading the state. We should fix it to know when LS is
            # ready.
            self.wait_for_app_launch(self._app, pause_after_launch=4)

        self.show_hints_message('EXPLANATION')
        self._app.set_level(5)

        try:
            self._app.set_object_property('view.JSContext.globalParameters',
                                          'updateSpinnerCode',
                                          '''if (enemy.position.y < 1000)
    enemy.position.y = enemy.position.y - 10;''')
        except Exception as e:
            logger.error('Error setting the code in LightSpeed: %s', e.message)
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_code(self):
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        self._app.reveal_topic('updateSpinner')

        self.show_hints_message('CODE')

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code

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
            return self.step_wait_for_flip
        if min_y < -20:
            self.show_hints_message('GOINGDOWN')
            return self.step_wait_for_flip
        if min_y > 10:
            self.show_hints_message('NOTREACHINGBOTTOM')
            return self.step_wait_for_flip
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
