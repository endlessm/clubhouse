from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class PowerUpB1(Quest):

    CHECK_GOAL_TIMEOUT = 20

    def __init__(self):
        super().__init__('PowerUpB1', 'saniel')
        self.auto_offer = True
        self._app = LightSpeed()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)

        self._app.reveal_topic('spawnEnemy')
        self._app.reveal_topic('spawnPowerup')
        self._app.set_level(12)

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
        self.show_hints_message('CODE')

        if self._app.get_js_property('flipped'):
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_abouttoplay

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_abouttoplay(self, message_id='ABOUTTOPLAY'):
        if not self._app.get_js_property('playing'):
            self.show_hints_message(message_id)
            self.wait_for_app_js_props_changed(self._app, ['playing', 'flipped'])

        if self._app.get_js_property('flipped'):
            return self.step_code

        self.reset_hints_given_once()
        return self.step_play, 'PLAYTEST'

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_play(self, message_id=None):
        if message_id:
            self.show_hints_message(message_id, give_once=True)

        self.wait_for_app_js_props_changed(self._app, [*self._app.POWERUPS_SPAWN_COUNTERS,
                                                       'playing',
                                                       'flipped'], timeout=self.CHECK_GOAL_TIMEOUT)

        if self._app.get_js_property('flipped'):
            # Player flipped the app:
            return self.step_code

        if not self._app.get_js_property('playing'):
            # Player crashed the ship:
            return self.step_abouttoplay, 'PLAY_AGAIN'

        spawned = self._app.get_powerups_spawned_dict('invulnerable', 'blowup')
        if spawned['invulnerable'] and spawned['blowup']:
            # Pause one second to see the spawned powerup on screen:
            self.pause(1)
            return self.step_success
        elif spawned['invulnerable'] or spawned['blowup']:
            # Pause one second to see the spawned powerup on screen:
            self.pause(1)
            return self.step_play, 'ONETYPEONLY'

        # Timeout reached and nothing was spawned, and player didn't
        # crash or flipped the app:
        return self.step_play, 'NOPOWERUPS'

    def step_success(self):
        Sound.play('quests/step-forward')
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
