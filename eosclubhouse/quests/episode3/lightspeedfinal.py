from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightspeedFinal(Quest):

    __items_on_completion__ = {'item.fob.2': {'consume_after_use': True}}

    def __init__(self):
        super().__init__('LightspeedFinal', 'saniel')
        self.auto_offer = True
        self._app = LightSpeed()

    def _all_enemies_spawned(self):
        return all(self._app.get_js_property('enemyType{}SpawnedCount'.format(i), 0) > 0
                   for i in range(4))

    def step_begin(self):
        self.ask_for_app_launch(self._app)

        self._app.reveal_topic('spawn')
        self._app.reveal_topic('activatePowerup')
        self._app.set_level(14)

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

        self.wait_for_app_js_props_changed(self._app, ['playing', 'success', 'flipped'])

        if self._app.get_js_property('flipped'):
            # Player flipped the app:
            return self.step_code

        if self._app.get_js_property('success'):
            # Player completed the level:
            if self._all_enemies_spawned():
                return self.step_success
            else:
                return self.step_play, 'NOTFOUR'

        if not self._app.get_js_property('playing'):
            # Player crashed the ship:
            return self.step_abouttoplay, 'PLAY_AGAIN'

        # This should not be reached unless the waiter times out:
        return self.step_play

    def step_success(self):
        self.give_item('item.fob.2', consume_after_use=True)
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
