from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class FizzicsIntro(Quest):

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada')
        self._app = Fizzics()

    def get_current_level(self):
        return self._app.get_effective_level(self.debug_skip())

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=1)
        return self.step_explanation

    def _connect_level_changed(self):
        return self.connect_app_props_changes(self._app, ['effectiveLevel'])

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_check_level(self):
        level = self.get_current_level()

        if level == 1:
            self.show_hints_message('LEVEL1')
        elif level == 2:
            Sound.play('quests/step-forward')
            self.show_hints_message('LEVEL2')
        else:
            self.wait_confirm('SUCCESS')
            return self.step_key

        async_action = self._connect_level_changed().wait()
        if async_action.is_cancelled():
            return self.abort

        return self.step_check_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
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
