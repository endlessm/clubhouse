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
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLANATION')
        self._app.set_level(5)
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

        self.show_hints_message('CODE')

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_play(self):
        self.show_hints_message('PLAYING')
        self.pause(10)

        while not self.is_cancelled():
            min_y = self._app.get_js_property('enemyType1MinY')
            max_y = self._app.get_js_property('enemyType1MaxY')

            if self.debug_skip():
                return self.step_success

            if min_y is not None and max_y is not None:
                if min_y >= -10 and max_y >= 0:
                    return self.step_success
                if min_y == max_y:
                    self.show_hints_message('NOTMOVING')
                    break
                if min_y < -20:
                    self.show_hints_message('GOINDOWN')
                    break

            self.wait_for_app_js_props_changed(self._app,
                                               ['enemyType1MinY', 'enemyType1MaxY'])

        return self.step_wait_for_flip

    def step_success(self):
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()
        self.stop()
