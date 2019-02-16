from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, Sound


class LightSpeedEnemyA1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyA1', 'ada')
        self._app = LightSpeed()
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("LightSpeedFix2"):
            self.available = True

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_newlevel
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_delay

    def step_delay(self, time_in_step):
        if time_in_step >= 2:
            return self.step_newlevel

    def step_newlevel(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('NEWLEVEL')
            available_levels = max(self._app.get_js_property('availableLevels'), 5)
            self._app.set_js_property('availableLevels', ('i', available_levels))
            self._app.set_js_property('currentLevel', ('i', 4))

        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_changeenemy

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_changeenemy(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CHANGEENEMY')

        if not self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_play

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_play(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('PLAY')

        enemy_count = self._app.get_js_property('obstacleType1SpawnedCount')
        if enemy_count >= 2 or self.debug_skip():
            # @todo: Check if they spawned asteroids and go back
            # @todo: Timeout if nothing spawned in 5 seconds
            return self.step_success

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('SUCCESS', confirm_label='Bye')
            Sound.play('quests/quest-complete')

        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
