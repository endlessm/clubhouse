from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class BonusRound(Quest):

    __available_after_completing_quests__ = ['MazePt4']

    # Dummy code to stub in quest
    def __init__(self):
        super().__init__('BonusRound', 'riley')

    def step_begin(self):
        self.wait_confirm('DUMMY1')
        self.wait_confirm('DUMMY2')
        return self.step_inlevel

    def step_inlevel(self):
        # there will be a bunch more levels here
        # different challenges than before
        return self.step_success

    def step_success(self):
        # give the Sidetrack level editing key
        self.give_item('item.key.sidetrack.3')
        self.wait_confirm('DUMMY3')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
