from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class StealthDevice(Quest):

    def __init__(self):
        super().__init__('StealthDevice', 'faber')
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("Hackdex2Decrypt"):
            self.available = True

    def step_begin(self):
        self.wait_confirm('RILEYQUESTION')
        self.wait_confirm('EXPLANATION')
        self.wait_confirm('RILEYTROUBLE')
        self.wait_confirm('EXPLANATION2')
        return self.step_end

    def step_end(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
