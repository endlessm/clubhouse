from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
# from eosclubhouse.apps import Maze


class MazePt3(Quest):

    def __init__(self):
        super().__init__('MazePt3', 'ada')
        # self._app = Maze()

    def step_begin(self):
        self.wait_confirm('HELLO')
        self.wait_confirm('HELLO2')
        self.show_hints_message('RILEYPUSH')
        self.pause(10)
        self.wait_confirm('RILEYPUSH2')
        self.wait_confirm('RILEYPUSH3')
        self.wait_confirm('RILEYPUSH4')
        self.wait_confirm('RILEYPUSH5')
        self.wait_confirm('RILEYPUSH6')
        self.wait_confirm('RILEYPUSH7')
        self.wait_confirm('RILEYPUSH8')
        self.wait_confirm('FELIXINTRO')
        self.wait_confirm('FELIXINTRO1')
        self.wait_confirm('FELIXINTRO2')
        self.wait_confirm('FELIXINTRO3')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
