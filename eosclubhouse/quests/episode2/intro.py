from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Intro(Quest):

    def __init__(self):
        super().__init__('Intro', 'riley')

    def step_begin(self):
        self.show_message('EXPLANATION')

        while (self.clubhouse_state.current_page != self.clubhouse_state.Page.EPISODES and
               not self.is_cancelled()):
            self.connect_clubhouse_changes(['current-page']).wait()

        return self.step_success

    def step_success(self):
        self.show_confirm_message('EPISODESTAB', confirm_label='Bye').wait()

        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')

        self.stop()
