from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LostFiles(Quest):

    __available_after_completing_quests__ = ['Hackdex1']

    def __init__(self):
        super().__init__('Lost Files', 'ada')

    def step_begin(self):
        self.wait_confirm('EXPLANATION1')
        self.wait_confirm('EXPLANATION2')
        self.wait_confirm('EXPLANATION3')

        self.show_message('EXPLANATION4', choices=[('End of Episode 1', self.finish_episode)])

    def finish_episode(self):
        Sound.play('quests/quest-complete')
        self.conf['complete'] = True
        self.available = False
        self.complete_current_episode()
        self.stop()
