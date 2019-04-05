from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class FizzicsPuzzle2(Quest):

    def __init__(self):
        super().__init__('FizzicsPuzzle2', 'faber')
        self._app = Fizzics()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_goal

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_goal(self):
        self.show_hints_message('GOAL')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.give_item('item.fob.3', consume_after_use=True)
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
