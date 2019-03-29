from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class FizzicsPuzzle2(Quest):

    APP_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('FizzicsPuzzle2', 'faber')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_success

    def step_success(self):
        self.give_item('item.program.3')
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
