from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LostFiles(Quest):

    def __init__(self):
        super().__init__('Lost Files', 'ada', QS('LOSTFILES_QUESTION'))
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        # TODO: Add delay before offering this quest. Maybe 10-30
        # minutes after the Hackdex Corruption one?
        if self.is_named_quest_complete("HackdexCorruption"):
            self.available = True

    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('LOSTFILES_EXPLANATION'))
        if self.confirmed_step():
            return self.step_explanation2

    def step_explanation2(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('LOSTFILES_EXPLANATION2'), character_id='saniel')
        if self.confirmed_step():
            return self.step_explanation3

    def step_explanation3(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('LOSTFILES_EXPLANATION3'), character_id='riley')
        if self.confirmed_step():
            return self.step_explanation4

    def step_explanation4(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('LOSTFILES_EXPLANATION4'), character_id='saniel')
        if self.confirmed_step():
            return self.step_explanation5

    def step_explanation5(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('LOSTFILES_EXPLANATION5'),
                              choices=[('End of Episode 1', self._confirm_step)])
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()
