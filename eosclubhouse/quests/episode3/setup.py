from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class SetUp(Quest):

    def __init__(self):
        super().__init__('SetUp', 'saniel')

    def step_begin(self):
        self.wait_confirm('EXPLAIN')
        self.wait_confirm('EXPLAIN2')
        return self.step_success

    def step_success(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
