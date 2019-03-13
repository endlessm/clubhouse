from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsIntro(Quest):

    APP_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada')
        self._app = App(self.APP_NAME)
        self._level = -1

    def get_current_level(self):
        if self.debug_skip():
            self._level += 1
            return self._level

        success = False
        level = self._app.get_js_property('currentLevel')

        if level is None:
            level = -1
        else:
            success = self._app.get_js_property('levelSuccess')

        self._level = level

        if self._level != -1 and (success or self.debug_skip()):
            self._level += 1

        return self._level

    def step_begin(self):
        self._level = -1

        if self._app.is_running():
            return self.step_explanation

        self.show_hints_message('LAUNCH')

        Sound.play('quests/new-icon')
        Desktop.add_app_to_grid(self.APP_NAME)
        Desktop.focus_app(self.APP_NAME)

        self.wait_for_app_launch(self._app)

        # And delay the next step to let the game initialize its current level
        self.pause(1)
        return self.step_explanation

    def _connect_level_changed(self):
        return self.connect_app_js_props_changes(self._app, ['levelSuccess', 'currentLevel'])

    @Quest.with_app_launched(APP_NAME)
    def step_check_level(self):
        level = self.get_current_level()

        if level < 1:
            self.show_hints_message('LEVEL1')
        elif level == 1:
            Sound.play('quests/step-forward')
            self.show_hints_message('LEVEL2')
        else:
            self.wait_confirm('SUCCESS')
            return self.step_key

        async_action = self._connect_level_changed().wait()
        if async_action.is_cancelled():
            return self.abort

        return self.step_check_level

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        Sound.play('quests/step-forward')

        if self.get_current_level() > 2:
            return self.step_already_beat

        self.wait_for_one([self.show_confirm_message('EXPLANATION'), self._connect_level_changed()])

        return self.step_check_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        return self.step_key

    def step_already_beat(self):
        self.wait_confirm('ALREADYBEAT')
        return self.step_key

    def step_key(self):
        self.give_item('item.key.fizzics.1')
        self.wait_confirm('KEYAFTER')
        return self.step_riley

    def step_riley(self):
        self.wait_confirm('RILEY')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.show_message('END', choices=[('Bye', self.stop)])
        Sound.play('quests/quest-complete')
