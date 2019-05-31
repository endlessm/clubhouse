from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LostFiles(Quest):

    __available_after_completing_quests__ = ['Hackdex1']
    __complete_episode__ = True

    def step_begin(self):
        self.wait_confirm('EXPLANATION1')
        self.wait_confirm('EXPLANATION2')
        self.wait_confirm('EXPLANATION3')

        self.show_message('EXPLANATION4', choices=[('End of Episode 1', self.finish_episode)])

    def finish_episode(self):
        Sound.play('quests/quest-complete')
        self.complete = True
        self.available = False
        self.stop()
