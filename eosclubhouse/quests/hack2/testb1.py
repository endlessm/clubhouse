from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class TestB1(Quest):

    __quest_name__ = 'Web Quest #1'
    __tags__ = ['mission:saniel', 'pathway:web']
    __mission_order__ = 100
    __pathway_order__ = 100

    def step_begin(self):
        self.wait_confirm('BEGIN')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.show_message('END', choices=[('Bye', self.stop)])
        Sound.play('quests/quest-complete')
