from eosclubhouse.libquest import Quest
from eosclubhouse.utils import ClubhouseState


class Meet(Quest):

    __tags__ = ['pathway:games', 'difficulty:easy']
    __pathway_order__ = 10

    def setup(self):
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        self.wait_confirm('WELCOME1')
        self.wait_confirm('WELCOME2')
        return self.step_mainwindow

    def step_mainwindow(self):
        self.highlight_nav('CLUBHOUSE')
        self.wait_confirm('GOBACK')
        # explain the concept of the clubhouse
        self.highlight_nav('')
        self.wait_confirm('EXPLAIN_MAIN1')
        self.wait_confirm('EXPLAIN_MAIN2')
        return self.step_hackmode

    def step_hackmode(self):
        # explain hack mode and how it works
        self.wait_confirm('EXPLAIN_HACK1')
        self._clubhouse_state.hack_switch_highlighted = True
        for msgid in ['EXPLAIN_HACK2', 'EXPLAIN_HACK3', 'EXPLAIN_HACK4']:
            self.wait_confirm(msgid)
        self._clubhouse_state.hack_switch_highlighted = False
        return self.step_pathways

    def step_pathways(self):
        # explain pathways
        self.highlight_nav('PATHWAYS')
        self.wait_confirm('EXPLAIN_PATHWAYS1')
        self.wait_confirm('EXPLAIN_PATHWAYS2')
        self.highlight_nav('')
        return self.step_profile

    def step_profile(self):
        # explain the profile
        self._clubhouse_state.user_button_highlighted = True
        self.wait_confirm('EXPLAIN_PROFILE1')
        self._clubhouse_state.user_button_highlighted = False
        for msgid in ['EXPLAIN_PROFILE2', 'EXPLAIN_PROFILE3']:
            self.wait_confirm(msgid)

        # ask if player wants to change their name
        def _choice(choice_var):
            return choice_var

        action = self.show_choices_message('CHANGE_NAME_ASK', ('CHANGE_NAME_YES', _choice, True),
                                           ('CHANGE_NAME_NO', _choice, False)).wait()
        choice = action.future.result()

        if choice:
            for msgid in ['CHANGE_NAME1', 'CHANGE_NAME2', 'CHANGE_NAME3', 'CHANGE_NAME4']:
                self.wait_confirm(msgid)

        for msgid in ['END1', 'END2']:
            self.wait_confirm(msgid)
        self.wait_confirm('END3', confirm_label="See you!")
        return self.step_complete_and_stop
