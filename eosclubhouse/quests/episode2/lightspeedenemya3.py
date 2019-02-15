from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, Sound


class LightSpeedEnemyA3(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedEnemyA3', 'ada')
        self._app = LightSpeed()

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
            available_levels = max(self._app.get_js_property('availableLevels'), 5)
            self._app.set_js_property('availableLevels', ('i', available_levels))
            self._app.set_js_property('currentLevel', ('i', 4))

        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_code(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('CODE')

        if (not self._app.get_js_property('flipped') and self._app.get_js_property('playing')) \
           or self.debug_skip():
            return self.step_play

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_play(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('PLAYING')

        if time_in_step > 10:
            min_y = self._app.get_js_property('obstacleType1MinY')
            max_y = self._app.get_js_property('obstacleType1MaxY')
            if (min_y >= -10 and max_y >= 0) or self.debug_skip():
                return self.step_success
            if (min_y == max_y):
                return self.step_notmoving
            if (min_y < -20):
                return self.step_goingdown

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_notmoving(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('NOTMOVING')

        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code

        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_goingdown(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('GOINGDOWN')

        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_code

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
