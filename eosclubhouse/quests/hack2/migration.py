from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Desktop
from eosclubhouse.utils import ClubhouseState


class Migration(Quest):

    __tags__ = ['pathway:games', 'skillset:Veteran']

    def setup(self):
        self.skippable = True
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        for msgid in ['WELCOME', 'WELCOME2']:
            self.wait_confirm(msgid)
        return self.step_open_clubhouse

    def step_open_clubhouse(self):
        self.show_hints_message('OPENIT')
        Desktop.set_hack_icon_pulse(True)
        self.wait_for_app_in_foreground(App('com.hack_computer.Clubhouse'))
        return self.step_explain_old_apps

    def step_explain_old_apps(self):
        # explain what we did to the old apps
        for msgid in ['OLDSTUFF1', 'OLDSTUFF2', 'OLDSTUFF3',
                      'OLDSTUFF4', 'OLDSTUFF5']:
            self.wait_confirm(msgid)
        return self.step_explain_new_stuff

    def step_explain_new_stuff(self):
        # explain hack mode
        for msgid in ['NEWSTUFF', 'HACKMODE1', 'HACKMODE2',
                      'HACKMODE3', 'HACKMODE4', 'HACKMODE5']:
            self.wait_confirm(msgid)
        return self.step_explain_activities

    def step_explain_activities(self):
        # explain activities and how to play them
        for msgid in ['ACTIVITIES1', 'ACTIVITIES2', 'ACTIVITIES3']:
            self.wait_confirm(msgid)
        return self.step_explain_profile

    def step_explain_profile(self):
        # explain how the profile works and how to change your name
        self._clubhouse_state.user_button_highlighted = True
        self.wait_confirm('PROFILE1')
        self._clubhouse_state.user_button_highlighted = False
        for msgid in ['PROFILE2', 'PROFILE3']:
            self.wait_confirm(msgid)
        action = self.show_choices_message('PROFILE_ASK', ('PROFILE_POS', None, True),
                                           ('PROFILE_NEG', None, False)).wait()
        if action.future.result():
            for msgid in ['PROFILE_CHANGENAME1', 'PROFILE_CHANGENAME2',
                          'PROFILE_CHANGENAME3', 'PROFILE_CHANGENAME4']:
                self.wait_confirm(msgid)
        return self.step_last

    def step_last(self):
        self.wait_confirm('END1')
        self.wait_confirm('END2')
        return self.step_complete_and_stop
