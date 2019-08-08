from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Meet(Quest):
    # Meet The Clubhouse

    __tags__ = ['mission:ada']

    __auto_offer_info__ = {'confirm_before': False, 'start_after': 3}

    def setup(self):
        self.auto_offer = True

    def step_begin(self):
        self.wait_confirm('WELCOME1')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.show_message('END3', choices=[('Bye', self.stop)])
        Sound.play('quests/quest-complete')
