from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class TestA3(Quest):

    __quest_name__ = 'Game Quest #3'
    __tags__ = ['mission:ada', 'pathway:games']
    __mission_order__ = 200
    __pathway_order__ = 300

    def step_begin(self):
        self.wait_confirm('BEGIN')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.show_message('END', choices=[('Bye', self.stop)])
        Sound.play('quests/quest-complete')
