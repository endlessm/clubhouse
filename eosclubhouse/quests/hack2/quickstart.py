from eosclubhouse.libquest import Quest


class Quickstart(Quest):

    __quest_name__ = 'Tutorial - The Clubhouse - Quickstart'
    __tags__ = ['mission:ada']
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
            for msgid in ['HACKSWITCH', 'PATHWAYS1', 'PATHWAYS2', 'PROFILE1', 'PROFILE2', 'END1']:
                self.wait_confirm(msgid)
        else:
            self.wait_confirm('DECLINE')

        self.show_message('END2', choices=[('Got it!', self.step_complete_and_stop)])
