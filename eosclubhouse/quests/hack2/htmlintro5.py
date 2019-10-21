from eosclubhouse.libquest import Quest
import os


class HTMLIntro5(Quest):

    __quest_name__ = "HTML - Div-ision of Labor"
    __tags__ = ['mission:riley', 'pathway:web', 'difficulty:easy']
    __pathway_order__ = 505

    TOTAL_MESSAGES = 29

    def setup(self):
        return self.step_begin

    def step_begin(self):
        self.wait_confirm('1')
        self.wait_confirm('2')
        os.system('xdg-open https://codepen.io/madetohack/pen/LYYxzOo?editors=1000')
        return self.step_main_loop, 3

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            self.wait_confirm('END')
            return self.step_complete_and_stop
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        action = self.show_choices_message(message_id, ('BAK', None, -1),
                                           ('FWD', None, 1)).wait()
        message_index += action.future.result()

        return self.step_main_loop, message_index
