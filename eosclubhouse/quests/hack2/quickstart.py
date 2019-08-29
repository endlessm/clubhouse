from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Quickstart(Quest):

    __quest_name__ = 'Tutorial - The Clubhouse'
    __tags__ = ['mission:ada']
    __mission_order__ = 10

    def step_begin(self):
        self.wait_confirm('WELCOME1')
        yesgo = ('POSITIVE', self.step_explain, True)
        notnow = ('NEGATIVE', self.step_explain, False)
        # this function needs a wait() to prevent a hang after the callback
        self.show_choices_message('WELCOME2', yesgo, notnow).wait()
        # returning from yes/no
        self.wait_confirm('END1')
        self.show_message('END2', choices=[('Got it!', self.step_end)])

    def step_explain(self, result):
        if result:
            for msgid in ['HACKSWITCH', 'PATHWAYS1', 'PATHWAYS2', 'PROFILE1', 'PROFILE2']:
                self.wait_confirm(msgid)

    def step_end(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
