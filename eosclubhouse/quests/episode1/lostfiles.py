from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LostFiles(Quest):

    def __init__(self):
        super().__init__('Lost Files', 'ada')
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        # TODO: Add delay before offering this quest. Maybe 10-30
        # minutes after the Hackdex Corruption one?
        if self.is_named_quest_complete("Hackdex1"):
            self.available = True

    def step_begin(self):
        self.wait_confirm('EXPLANATION1')
        self.wait_confirm('EXPLANATION2')
        self.wait_confirm('EXPLANATION3')

        self.show_message('EXPLANATION4', choices=[('End of Episode 1', self.finish_episode)])

    def finish_episode(self):
        Sound.play('quests/quest-complete')
        self.conf['complete'] = True
        self.complete_current_episode()
        self.stop()

