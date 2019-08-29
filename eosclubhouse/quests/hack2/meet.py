from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Meet(Quest):

    __quest_name__ = 'DEBUG NAME - Meet - DEBUG NAME'
    __tags__ = ['mission:ada']
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 3}

    def setup(self):
        self.auto_offer = True
        # Hide quest in UI
        self.skippable = True

    def step_begin(self):

        resume_at_step = self.get_named_quest_conf('Meet', 'resume_step')

        if resume_at_step == "main":
            return self.step_mainwindow
        elif resume_at_step == "hack":
            return self.step_hackmode
        elif resume_at_step == "path":
            return self.step_pathways
        elif resume_at_step == "profile":
            return self.step_profile
        elif resume_at_step == "end":
            return self.step_end
        else:
            self.wait_confirm('WELCOME1')
            self.wait_confirm('WELCOME2')
            # check to see if the player got a hint in the initial puzzle
            # (this is intended to reward existing users who know the puzzle from hack 1.0)
            if self.get_named_quest_conf('FirstContact', 'puzzle_hint_given'):
                msg_id = 'WELCOME3_GOTHINT'
            else:
                msg_id = 'WELCOME3_NOHINT'
            self.wait_confirm(msg_id)
            return self.step_mainwindow

    def step_mainwindow(self):
        self.set_conf('resume_step', 'main')
        self.save_conf()
        # explain the concept of the clubhouse
        self.wait_confirm('EXPLAIN_MAIN1')
        self.wait_confirm('EXPLAIN_MAIN2')
        return self.step_hackmode

    def step_hackmode(self):
        # explain hack mode and how it works
        self.set_conf('resume_step', 'hack')
        self.save_conf()
        for msgid in ['EXPLAIN_HACK1', 'EXPLAIN_HACK2', 'EXPLAIN_HACK3', 'EXPLAIN_HACK4']:
            self.wait_confirm(msgid)
        return self.step_pathways

    def step_pathways(self):
        # explain pathways
        self.set_conf('resume_step', 'path')
        self.save_conf()
        self.wait_confirm('EXPLAIN_PATHWAYS1')
        self.wait_confirm('EXPLAIN_PATHWAYS2')
        return self.step_profile

    def step_profile(self):
        # explain the profile
        self.set_conf('resume_step', 'profile')
        self.save_conf()
        for msgid in ['EXPLAIN_PROFILE1', 'EXPLAIN_PROFILE2', 'EXPLAIN_PROFILE3']:
            self.wait_confirm(msgid)
        # ask if player wants to change their name
        showme = ('CHANGE_NAME_YES', self.step_changename, True)
        notnow = ('CHANGE_NAME_NO', self.step_changename, False)
        # this function needs a wait() to prevent a hang after the callback
        self.show_choices_message('CHANGE_NAME_ASK', showme, notnow).wait()
        return self.step_end

    def step_changename(self, result):
        if result:
            for msgid in ['CHANGE_NAME1', 'CHANGE_NAME2', 'CHANGE_NAME3', 'CHANGE_NAME4']:
                self.wait_confirm(msgid)

    def step_end(self):
        self.set_conf('resume_step', 'end')
        self.save_conf()
        self.wait_confirm('END1')
        self.wait_confirm('END2')
        self.complete = True
        self.available = False
        self.show_message('END3', choices=[('Got it!', self.stop)])
        Sound.play('quests/quest-complete')
