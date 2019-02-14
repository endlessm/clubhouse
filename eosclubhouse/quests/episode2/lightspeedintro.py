from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class LightSpeedIntro(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeed Intro', 'ada')
        self._app = App(self.APP_NAME)

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
            # If no delay were added, step-begin sound would overlap shadow
            # the 'new icon' sound.
            Desktop.add_app_to_grid(self.APP_NAME, delay=3)
            Desktop.focus_app(self.APP_NAME)

            self.wait_for_app_launch(self._app)

        return self.step_explanation

    def step_abort(self):
        Sound.play('quests/quest-aborted')
        self.show_message('ABORT')
        self.pause(5)
        self.stop()

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')
        return self.step_check_score

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_check_score(self):
        old_level = self._level
        level = self.get_current_score()
        message_id = None

        # Check if the player lost and got to 0 points
        if level == 0 and old_level > level:
            message_id = 'GOAL'
        elif level == 1:
            message_id = 'ONE'
        elif level == 3:
            message_id = 'THREE'
        elif level >= 5:
            return self.step_end

        if message_id is not None:
            self.show_hints_message(message_id)

        self.wait_for_app_js_props_changed(self._app, ['score'])
        return self.step_check_score

    def step_end(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        self.stop()
