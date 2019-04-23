from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound

class LeviHackdex(Quest):
# Dummy code to stub in quest
    def __init__(self):
        super().__init__('LeviHackdex', 'ada')

    def step_begin(self):
        self.wait_confirm('OPENINTRO')
        self.wait_confirm('OPENINTRO1')
        self.wait_confirm('OPENINTRO2')
        self.wait_confirm('GIVEKEY')
        self.wait_confirm('BACKGROUND')
        self.wait_confirm('PUSHINSTRUCTION')
        self.wait_confirm('PUSHINSTRUCTION2')
        self.wait_confirm('PUSHINSTRUCTION3')
        return self.step_success

    def step_success(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
