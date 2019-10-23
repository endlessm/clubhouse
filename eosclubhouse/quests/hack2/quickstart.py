from eosclubhouse.libquest import Quest


class Quickstart(Quest):

    __tags__ = ['pathway:games']
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 3}
    __available_after_completing_quests__ = ['FirstContact']

    def setup(self):
        self.auto_offer = True
        # Hide quest in UI
        self.skippable = True

    def step_begin(self):
        self.wait_confirm('WELCOME1')

        def _choice(choice_var):
            return choice_var

        action = self.show_choices_message('WELCOME2', ('POSITIVE', _choice, True),
                                           ('NEGATIVE', _choice, False)).wait()
        choice = action.future.result()

        if choice:
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
