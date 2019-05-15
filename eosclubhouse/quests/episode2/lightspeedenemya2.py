from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedEnemyA2(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyA2', 'ada')
        self._app = LightSpeed()

    def step_begin(self):
        self._app.reveal_topic('spawn')

        self.ask_for_app_launch(self._app)

        self.show_hints_message('EXPLANATION')
        self._app.set_level(5)
        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self, msg_id='CODE'):
        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_code, msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_code(self, msg_id):
        # Use a local variable so we can reassign it if the player is in the Restart/Continue
        # screens without the message getting propagated the next time step_code is called.
        msg_to_show = msg_id

        if not self._app.get_js_property('flipped') or self.debug_skip():
            if self._app.get_js_property('playing'):
                return self.step_play

            # If we're not flipped nor playing, then we're in a Restart or Continue screens, and
            # thus ask the user to play.
            msg_to_show = 'ASK_PLAY'

        self._app.reveal_topic('updateSpinner')

        self.show_hints_message(msg_to_show)

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'])
        return self.step_code, msg_id

    @Quest.with_app_launched(APP_NAME)
    def step_play(self):
        self.show_hints_message('PLAYING')

        enemy_count_start = self._app.get_js_property('enemyType1SpawnedCount', 0)

        self.wait_for_app_js_props_changed(self._app, [
            'enemyType1SpawnedCount',
            'flipped',
            'playing',
        ], timeout=10)

        enemy_count_end = self._app.get_js_property('enemyType1SpawnedCount', 0)

        if self._app.get_js_property('flipped') or not self._app.get_js_property('playing'):
            # step_code is actually "is flipped or is in a Restart or Continue screen"
            return self.step_code, 'CODE'

        if enemy_count_start < enemy_count_end:
            # The enemy was spawned, advance:
            return self.step_check_direction

        # The waiter timed out and enemy didn't spawn:
        self.show_hints_message('NOENEMIES')
        return self.step_wait_for_flip, 'ADD_ENEMY_CODE'

    def step_check_direction(self):
        min_y_start = self._app.get_js_property('enemyType1MinY')
        max_y_start = self._app.get_js_property('enemyType1MaxY')

        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing'], timeout=10)

        min_y_end = self._app.get_js_property('enemyType1MinY')
        max_y_end = self._app.get_js_property('enemyType1MaxY')

        if self._app.get_js_property('flipped') or not self._app.get_js_property('playing'):
            # step_code is actually "is flipped or is in a Restart or Continue screen"
            return self.step_code, 'CODE'

        # The waiter timed out, so we can test if it moved more to the
        # up or down:

        if min_y_start == min_y_end and max_y_start == max_y_end:
            self.show_hints_message('NOTMOVING')
            return self.step_wait_for_flip

        going_up = abs(min_y_start - min_y_end) > abs(max_y_start - max_y_end)

        if going_up:
            self.show_hints_message('GOINGUP')
            return self.step_wait_for_flip

        # Otherwise it must be going down, and this is the goal of the
        # quest:
        return self.step_success

    def step_success(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()
        self.stop()
