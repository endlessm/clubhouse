from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class StealthDevice(Quest):

    def __init__(self):
        super().__init__('StealthDevice', 'faber')
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("Hackdex2Decrypt"):
            self.available = True

    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_question('RILEYQUESTION')
        if self.confirmed_step():
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question('EXPLANATION')
        if self.confirmed_step():
            return self.step_rileytrouble

    def step_rileytrouble(self, time_in_step):
        if time_in_step == 0:
            self.show_question('RILEYTROUBLE')
        if self.confirmed_step():
            return self.step_explanation2

    def step_explanation2(self, time_in_step):
        if time_in_step == 0:
            self.show_question('EXPLANATION2')
        if self.confirmed_step():
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('END', confirm_label='Bye')
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()
