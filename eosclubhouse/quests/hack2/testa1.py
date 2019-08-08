from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class TestA1(Quest):

    __quest_name__ = 'Game Quest #1'
    __tags__ = ['mission:ada', 'pathway:games', 'difficulty:normal']
    __mission_order__ = 100
    __pathway_order__ = 100

    def step_begin(self):
        self.show_message('NARRATIVE_A', narrative=True)
        self.pause(3)
        self.show_message('NARRATIVE_B', narrative=True)
        self.pause(3)
        self.dismiss_message(narrative=True)
        self.pause(1)
        # @todo: Check why the button isn't displayed the first time,
        # allocation issues.
        # self.wait_confirm('NARRATIVE_C', narrative=True, confirm_label='Next')
        return self.step_again(first_try=True)

    def step_again(self, first_try=False, said_yes=False):
        if first_try:
            message_id = 'NARRATIVE_START'
        else:
            message_id = 'NARRATIVE_YES' if said_yes else 'NARRATIVE_NO'
        self.show_message(message_id, narrative=True,
                          choices=[
                              ('Yes', self.step_again, False, True),
                              ('No', self.step_again, False, False),
                              ('Bye', self.step_end),
                          ])

    def step_end(self):
        self.dismiss_message(narrative=True)
        self.complete = True
        self.available = False
        self.show_message('END', choices=[('Bye', self.stop)])
        Sound.play('quests/quest-complete')
