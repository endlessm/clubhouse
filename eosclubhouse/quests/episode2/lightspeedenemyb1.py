from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class LightSpeedEnemyB1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'
    SCREEN_HEIGHT = 1004

    def __init__(self):
        super().__init__('LightSpeedEnemyB1', 'saniel')
        self._app = App(self.APP_NAME)

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_explanation
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_delay

    def step_delay(self, time_in_step):
        if time_in_step >= 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('EXPLANATION')
            levelCount = self._app.get_js_property('availableLevels')
            levelCount = max(levelCount, 6)
            self._app.set_js_property('availableLevels', ('i', levelCount))
            self._app.set_js_property('currentLevel', ('i', 6))
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code1
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_code1(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE1')
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
                or self.debug_skip():
            return self.step_playtest

    def step_playtest(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('PLAYTEST')
        if time_in_step > 10:
            enemyCount = self._app.get_js_property('obstacleType2SpawnedCount')
            if enemyCount == 0:
                return self.step_noenemy
            minY = self._app.get_js_property('obstacleType2MinY')
            maxY = self._app.get_js_property('obstacleType2MaxY')
            if (minY == maxY):
                return self.step_notmoving
            if (minY < -100 or maxY > self.SCREEN_HEIGHT + 100):
                return self.step_offscreen
            if (maxY - minY <= 2.1):
                return self.step_smallmovement
            return self.step_success
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_noenemy(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('NOENEMY')
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code1
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_notmoving(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('NOTMOVING')
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code2
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_offscreen(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('OFFSCREEN')
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code2
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_smallmovement(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('SMALLMOVEMENT')
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code3
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_code2(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE2')
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
                or self.debug_skip():
            return self.step_playtest
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_code3(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE3')
        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
                or self.debug_skip():
            return self.step_playtest
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
