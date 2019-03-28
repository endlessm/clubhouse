from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class ApplyFob1(Quest):

    def __init__(self):
        super().__init__('ApplyFob1', 'ada')

    def step_begin(self):
        return self.step_success

    def step_success(self):
        self.wait_confirm('END')
        Sound.play('quests/quest-complete')
        self.complete = True
        self.available = False
        self.stop()
