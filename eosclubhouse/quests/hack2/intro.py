from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Intro(Quest):

    __tags__ = ['mission:ada']

    __auto_offer_info__ = {'confirm_before': False, 'start_after': 3}

    def setup(self):
        self.auto_offer = True

    def step_begin(self):
        self.wait_confirm('WELCOME')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.show_message('END', choices=[('Bye', self.stop)])
        Sound.play('quests/quest-complete')
