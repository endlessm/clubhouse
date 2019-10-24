from eosclubhouse.libquest import Quest
from eosclubhouse.utils import ClubhouseState


class Quickstart(Quest):

    __tags__ = ['pathway:games']
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 0}
    __available_after_completing_quests__ = ['FirstContact']

    def setup(self):
        self.auto_offer = True
        # Hide quest in UI
        self.skippable = True
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        # Disable the entire Clubhouse UI until the player chooses
        # between accept or decline the quickstart:
        self._clubhouse_state.window_is_disabled = True

        self.wait_confirm('WELCOME1')

        action = self.show_choices_message('WELCOME2', ('POSITIVE', None, True),
                                           ('NEGATIVE', None, False)).wait()

        # Mark the quest as complete and save it to the game state
        # before finishing, because the player already decided:
        self.complete = True
        self.save_conf()
        self._clubhouse_state.window_is_disabled = False

        if action.future.result():
            self.highlight_nav('CLUBHOUSE')
            self.wait_confirm('HACKSWITCH1')
            self.highlight_nav('')
            self.wait_confirm('HACKSWITCH2')
            self.wait_confirm('HACKSWITCH3')
            self.highlight_nav('PATHWAYS')
            self.wait_confirm('PATHWAYS1')
            self.wait_confirm('PATHWAYS2')
            self.highlight_nav('')
            self.wait_confirm('PROFILE1')
            self.wait_confirm('PROFILE2')
        else:
            self.wait_confirm('DECLINE')

        self.show_message('END1', choices=[('Will do!', self.step_complete_and_stop)])

    def step_abort(self):
        # This is in case the quest is aborted between the
        # disable/enable of the window:
        self._clubhouse_state.window_is_disabled = False
        super().step_abort()
