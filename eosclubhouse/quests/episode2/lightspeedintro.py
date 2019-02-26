from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class LightSpeedIntro(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeed Intro', 'ada')
        self._app = App(self.APP_NAME)
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete('Intro'):
            self.available = True

    def get_current_score(self):
        if self.debug_skip():
            self._level += 1
        else:
            self._level = self._app.get_js_property('score', 0)
        return self._level

    def step_begin(self):
        self._level = 0

        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            Desktop.add_app_to_grid(self.APP_NAME)
            Desktop.focus_app(self.APP_NAME)

            self.wait_for_app_launch(self._app)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')
        return self.step_check_score

    @Quest.with_app_launched(APP_NAME)
    def step_check_score(self):
        old_level = self._level
        level = self.get_current_score()
        message_id = None

        # Check if the player lost and got to 0 points
        if level == 0 and old_level > level:
            message_id = 'GOAL'
        elif level == 1:
            message_id = 'ONE'
        elif level == 2:
            message_id = 'TWO'
        elif level >= 3:
            return self.step_end

        if message_id is not None:
            self.show_hints_message(message_id)

        self.wait_for_app_js_props_changed(self._app, ['score'])
        return self.step_check_score

    def step_end(self):
        self.wait_confirm('SUCCESS')

        self.give_item('item.key.lightspeed.1')
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
