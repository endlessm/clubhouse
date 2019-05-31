from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class StealthDevice(Quest):

    def step_begin(self):
        self.wait_confirm('RILEYQUESTION')
        self.wait_confirm('EXPLANATION')
        self.wait_confirm('RILEYTROUBLE')
        self.wait_confirm('EXPLANATION2')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
