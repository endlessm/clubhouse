from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class AdaQuest1(Quest):

    APP_NAME = 'com.endlessm.Sidetrack'

    def __init__(self):
        super().__init__('AdaQuest1', 'ada')
        self._app = App(self.APP_NAME)
        self.depth_flag = False

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_main

    def set_depth_flag(self, value):
        self.depth_flag = True if value else False

    @Quest.with_app_launched(APP_NAME)
    def show_deepness(self, offer, deep_messages):
        proceed = ('PROCEED', self.set_depth_flag, True)
        cancel = ('CANCEL', self.set_depth_flag, False)
        self.show_choices_message(offer, proceed, cancel).wait()
        if self.depth_flag:
            for message in deep_messages:
                self.wait_confirm(message)
        else:
            self.wait_confirm('REVENON')

    @Quest.with_app_launched(APP_NAME)
    def step_main(self):
        self.show_deepness('INITIALTEXT', ['DEEPTEXT1', 'DEEPTEXT2', 'DEEPTEXT3'])
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        # self.complete = True
        # self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
