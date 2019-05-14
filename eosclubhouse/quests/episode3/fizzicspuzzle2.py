from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class FizzicsPuzzle2(Quest):

    GAME_PRESET = 1004

    def __init__(self):
        super().__init__('FizzicsPuzzle2', 'faber')
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
        self.wait_for_app_js_props_changed(self._app, ['quest4Success'])
        if self._app.get_js_property('quest4Success') or self.debug_skip():
            self.wait_confirm('SUCCESS')
            self.give_item('item.fob.3', consume_after_use=True)
            return self.step_end

        return self.step_play

    def step_end(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
