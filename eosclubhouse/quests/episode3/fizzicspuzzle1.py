from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class FizzicsPuzzle1(Quest):

    __available_after_completing_quests__ = ['ApplyFob2']
    GAME_PRESET = 1003

    def __init__(self):
        super().__init__('FizzicsPuzzle1', 'faber')
        self._app = Fizzics()

    def step_begin(self):
        self.ask_for_app_launch(self._app)
        return self.step_goal

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_goal(self):
        self._app.set_js_property('preset', ('i', self.GAME_PRESET))
        self.show_hints_message('GOAL')
        return self.step_play

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_play(self):
        self.wait_for_app_js_props_changed(self._app, ['quest3Success'])
        if self._app.get_js_property('quest3Success') or self.debug_skip():
            self.wait_confirm('SUCCESS')
            return self.step_end

        return self.step_play

    def step_end(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
