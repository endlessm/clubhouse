from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Intro(Quest):

    def __init__(self):
        super().__init__('Intro', 'riley')

    def step_begin(self):
        self.show_confirm_message('EXPLANATION').wait()
        # TODO: Wait for clicking on the Episodes tab on the Clubhouse
        self.show_confirm_message('EPISODESTAB', confirm_label='Bye').wait()

        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')

        self.stop()
