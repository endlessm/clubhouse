from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, GameStateService
# from eosclubhouse.apps import Maze


class MazePt4(Quest):

    __available_after_completing_quests__ = ['FizzicsKey']
    __complete_episode__ = True

    def __init__(self):
        super().__init__('MazePt4', 'ada')
        self._gss = GameStateService()
        # self._app = Maze()

    def step_begin(self):
        self.wait_confirm('DUMMY1')
        self.wait_confirm('DUMMY2')
        return self.step_success

    def step_success(self):
        self.wait_confirm('DUMMY3')
        # Yay riley's back
        self._gss.set('clubhouse.character.Riley', {'in_trap', False})
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
