from eosclubhouse.libquest import Quest
from eosclubhouse.utils import ClubhouseState


class Quickstart(Quest):

    __tags__ = ['pathway:games']
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 0}
    __available_after_completing_quests__ = ['FirstContact']
    __dismissible_messages__ = False

    def setup(self):
        self.auto_offer = True
        # Hide quest in UI
        self.skippable = True
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        # Disable the characters in the UI to prevent launching any
        # other quest while the player is running the quickstart:
        self._clubhouse_state.characters_disabled = True

        self.wait_confirm('WELCOME1')

        action = self.show_choices_message('WELCOME2', ('POSITIVE', None, True),
                                           ('NEGATIVE', None, False)).wait()

        if action.future.result():
            self.highlight_nav('CLUBHOUSE')
            self.wait_confirm('HACKSWITCH1')
            self.highlight_nav('')

            # If the user played with the hack switch before the
            # explanation, we reset to normal:
            if not self._clubhouse_state.lights_on:
                self._clubhouse_state.lights_on = True

            self._clubhouse_state.hack_switch_highlighted = True
            self.show_message('HACKSWITCH2')
            self.connect_clubhouse_changes(['lights-on']).wait()
            self._clubhouse_state.hack_switch_highlighted = False
            self.show_message('HACKSWITCH3')
            self.connect_clubhouse_changes(['lights-on']).wait()

            self.highlight_nav('PATHWAYS')
            self.wait_confirm('PATHWAYS1')
            self.wait_confirm('PATHWAYS2')
            self.highlight_nav('')
            self.wait_confirm('PROFILE1')
            self.wait_confirm('PROFILE2')
        else:
            self.wait_confirm('DECLINE')

        self.show_message('END1', choices=[('Will do!', self.step_complete_and_stop)])

    def _back_to_normal(self):
        self._clubhouse_state.characters_disabled = False
        if not self._clubhouse_state.lights_on:
            self._clubhouse_state.lights_on = True

    def step_complete_and_stop(self):
        self._back_to_normal()
        super().step_complete_and_stop()

    def step_abort(self):
        self._back_to_normal()
        super().step_abort()
