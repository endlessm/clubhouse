from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedFix2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedFix2', 'saniel')
        self._app = LightSpeed()

    def step_begin(self):
        # Reveal this topic here, I guess? There's not really any other good
        # place to reveal it, because it's never used in any of the quests.
        self._app.reveal_topic('updateAsteroid')

        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')

        # @todo: Alert the user something was wrong is the level couldn't be set
        self._app.set_level(4)
        return self.step_wait_for_flip, 'CODE'

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self, msg_id):
        if msg_id == 'CODE':
            self._app.reveal_topic('spawnEnemy')

        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code, msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_code(self, msg_id):
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
        self.pause(4)

        enemyCount = self._app.get_js_property('enemyType0SpawnedCount') or 0

        if enemyCount > 10:
            self.show_hints_message('TOOMANY')
            return self.step_wait_for_flip, 'CODE2'

        if enemyCount > 0 or self.debug_skip():
            return self.step_success

        self.show_hints_message('NOENEMIES')
        return self.step_wait_for_flip, 'CODE'

    def step_success(self):
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        self.stop()
