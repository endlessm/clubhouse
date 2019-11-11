from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop
from eosclubhouse.utils import ClubhouseState


class Migration(Quest):

    __tags__ = ['pathway:games', 'skillset:Veteran']
    __dismissible_messages__ = False

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
        # @todo: we should use wait_for_app_in_foreground() here instead of
        # doing a busy wait, see https://phabricator.endlessm.com/T28521
        while not Desktop.is_app_in_foreground('com.hack_computer.Clubhouse'):
            self.pause(3)
        return self.step_explain_old_apps

    def step_explain_old_apps(self):
        self._clubhouse_state.characters_disabled = True
        # explain what we did to the old apps
        for msgid in ['OLDSTUFF1', 'OLDSTUFF2', 'OLDSTUFF3']:
            self.wait_confirm(msgid)
        self.complete = True
        for msgid in ['OLDSTUFF4', 'OLDSTUFF5']:
            self.wait_confirm(msgid)
        return self.step_explain_new_stuff

    def step_explain_new_stuff(self):
        # explain hack mode
        for msgid in ['NEWSTUFF', 'HACKMODE1', 'HACKMODE2']:
            self.wait_confirm(msgid)
        # If the user played with the hack switch before the
        # explanation, we reset to normal:
        if not self._clubhouse_state.lights_on:
            self._clubhouse_state.lights_on = True
        self._clubhouse_state.hack_switch_highlighted = True
        skip_action = self.show_confirm_message('HACKMODE3',
                                                confirm_label="I'd prefer not to, but thanks.")
        user_action = self.connect_clubhouse_changes(['lights-on'])
        self.wait_for_one([skip_action, user_action])
        self._clubhouse_state.hack_switch_highlighted = False
        if skip_action.is_done():
            # Automatically turn the lights off because the player
            # wants to skip using the switcher:
            self._clubhouse_state.lights_on = False
        skip_action = self.show_confirm_message('HACKMODE4', confirm_label='OK, I see.')
        user_action = self.connect_clubhouse_changes(['lights-on'])
        self.wait_for_one([skip_action, user_action])
        if skip_action.is_done():
            # Automatically turn the lights on because the player
            # wants to skip using the switcher:
            self._clubhouse_state.lights_on = True
        self._clubhouse_state.hack_switch_highlighted = False
        self.wait_confirm('HACKMODE5')
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
        self._clubhouse_state.characters_disabled = False
        return self.step_complete_and_stop
