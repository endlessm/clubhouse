from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class AdaQuest1(Quest):

    APP_NAME = 'com.endlessm.Sidetrack'

    def __init__(self):
        super().__init__('AdaQuest1', 'ada')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_main

    def cancel_deepness(self):
        self.wait_confirm('REVENON')
        # return self.step_success

    # def proceed_deeper(self, deep_messages):
    #     self.show_deepness(deep_messages)

    def show_deepness(self, deep_messages):
        message_id = deep_messages.pop(0)
        if message_id is not None:
            proceed = ('PROCEED', self.show_deepness(deep_messages), 1)
            cancel = ('CANCEL', self.cancel_deepness, 1)
            self.show_choices_message(message_id, proceed, cancel).wait()

    @Quest.with_app_launched(APP_NAME)
    def step_main(self):
        self.wait_confirm('INITIALTEXT')
        self.show_deepness(['DEEPTEXT1', 'DEEPTEXT2', 'DEEPTEXT3'])
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
