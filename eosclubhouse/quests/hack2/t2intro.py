from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class T2Intro(Quest):

    APP_NAME = 'com.endlessnetwork.frogsquash'

    __quest_name__ = 'Terminal 2 - FrogSquash'
    __tags__ = ['mission:saniel', 'pathway:games', 'difficulty:easy']
    __mission_order__ = 125
    __pathway_order__ = 125
    __auto_offer_info__ = {'confirm_before': True}

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if self.get_named_quest_conf('T2Intro', 'has_seen_intro'):
            return self.step_normalrun
        else:
            return self.step_firstrun

    def step_firstrun(self):
        self.wait_confirm('FIRSTRUN1')
        self.wait_confirm('FIRSTRUN2')
        self.set_conf('has_seen_intro', True)
        self.save_conf()
        self.show_message('FIRSTRUN3', choices=[('OK, got it.', self.step_normalrun)])

    def step_normalrun(self):
        self.wait_confirm('GREET1')
        self.show_message('GREET2', choices=[('Will do!', self.step_launch)])

    def step_launch(self):
        self.wait_confirm('BYE')
        Sound.play('quests/quest-complete')
        # We are about to launch a fullscreen app. So no messages
        # should be displayed after this point:
        self._app.launch()
        self.wait_for_app_launch(self._app, pause_after_launch=3)
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
