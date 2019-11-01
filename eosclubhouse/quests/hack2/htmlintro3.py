from eosclubhouse.libquest import Quest
import os


class HTMLIntro3(Quest):

    __tags__ = ['pathway:web', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 503

    TOTAL_MESSAGES = 26

    def setup(self):
        return self.step_begin

    def step_begin(self):
        self.wait_confirm('1')
        self.wait_confirm('2')
        os.system('xdg-open https://codepen.io/madetohack/pen/oNNYNXB?editors=1000#code-area')
        return self.step_main_loop, 3

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            self.wait_confirm('END')
            return self.step_complete_and_stop
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        action = self.show_choices_message(message_id, ('NOQUEST_NAV_BAK', None, -1),
                                           ('NOQUEST_NAV_FWD', None, 1)).wait()
        message_index += action.future.result()

        return self.step_main_loop, message_index
