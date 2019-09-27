from eosclubhouse.libquest import Quest


class Meet(Quest):

    __quest_name__ = 'Tutorial - The Clubhouse'
    __tags__ = ['mission:ada']
    __mission_order__ = 10

    def step_begin(self):
        self.wait_confirm('WELCOME1')
        self.wait_confirm('WELCOME2')
        return self.step_mainwindow

    def step_mainwindow(self):
        self.wait_confirm('GOBACK')
        # explain the concept of the clubhouse
        self.wait_confirm('EXPLAIN_MAIN1')
        self.wait_confirm('EXPLAIN_MAIN2')
        return self.step_hackmode

    def step_hackmode(self):
        # explain hack mode and how it works
        for msgid in ['EXPLAIN_HACK1', 'EXPLAIN_HACK2', 'EXPLAIN_HACK3', 'EXPLAIN_HACK4']:
            self.wait_confirm(msgid)
        return self.step_pathways

    def step_pathways(self):
        # explain pathways
        self.wait_confirm('EXPLAIN_PATHWAYS1')
        self.wait_confirm('EXPLAIN_PATHWAYS2')
        return self.step_profile

    def step_profile(self):
        # explain the profile
        for msgid in ['EXPLAIN_PROFILE1', 'EXPLAIN_PROFILE2', 'EXPLAIN_PROFILE3']:
            self.wait_confirm(msgid)

        # ask if player wants to change their name
        def _choice(choice_var):
            return choice_var

        action = self.show_choices_message('CHANGE_NAME_ASK', ('CHANGE_NAME_YES', _choice, True),
                                           ('CHANGE_NAME_NO', _choice, False)).wait()
        choice = action.future.result()

        if choice:
            for msgid in ['CHANGE_NAME1', 'CHANGE_NAME2', 'CHANGE_NAME3']:
                self.wait_confirm(msgid)

        for msgid in ['END1', 'END2', 'END3']:
            self.wait_confirm(msgid)
        return self.step_complete_and_stop
