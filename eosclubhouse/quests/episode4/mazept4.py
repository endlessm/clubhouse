from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Maze

class MazePt4(Quest):

    __available_after_completing_quests__ = ['FizzicsKey']
    # Dummy code to stub in quest
    def __init__(self):
        super().__init__('MazePt4', 'ada')

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