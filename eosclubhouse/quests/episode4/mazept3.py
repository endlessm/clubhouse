from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
# from eosclubhouse.apps import Maze


class MazePt3(Quest):

    def __init__(self):
        super().__init__('MazePt3', 'ada')
        # self._app = Maze()

    def step_begin(self):
        self.wait_confirm('DUMMY1')
        self.wait_confirm('DUMMY2')
        return self.step_success

    def step_success(self):
        self.wait_confirm('DUMMY3')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
