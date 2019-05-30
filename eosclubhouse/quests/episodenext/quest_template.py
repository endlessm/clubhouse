from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class QuestTemplate(Quest):

    __items_on_completion__ = {'item.key.testkey': {}}
    APP_NAME = 'com.endlessm.Sidetrack'

    def __init__(self):
        super().__init__('QuestTemplate', 'ada')
        self._app = App(self.APP_NAME)
        self.choiceval = False

    def do_choice(self, value):
        self.choiceval = value

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_part1

    @Quest.with_app_launched(APP_NAME)
    def step_part1(self):
        for message_id in ['TEXT1', 'TEXT2', 'TEXT3']:
            self.wait_confirm(message_id)
        return self.step_part2

    @Quest.with_app_launched(APP_NAME)
    def step_part2(self):
        self.show_hints_message('HELP1')
        self.pause(10)
        choice1 = ('ANS1', self.do_choice(True), 1)
        choice2 = ('ANS2', self.do_choice(False), 1)
        self.show_choices_message('CHOICEQUESTION', choice1, choice2).wait()

        self.wait_confirm('CHOICE1') if self.choiceval else self.wait_confirm('CHOICE2')
        self.give_item('item.key.testkey')
        self.wait_confirm('GIVEKEY')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
