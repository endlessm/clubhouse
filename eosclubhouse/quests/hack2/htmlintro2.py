from eosclubhouse.libquest import Quest
import os


class HTMLIntro2(Quest):

    __quest_name__ = "DEBUG - HTML Intro 2 - Colors"
    __tags__ = ['mission:riley', 'pathway:web', 'difficulty:easy']
    __pathway_order__ = 502

    TOTAL_MESSAGES = 23

    def setup(self):
        return self.step_begin

    def step_begin(self):
        self.wait_confirm('1')
        self.wait_confirm('2')
        os.system('xdg-open https://codepen.io/madetohack/pen/BaaNeXj?editors=1000#code-area')
        return self.step_main_loop, 3

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            self.wait_confirm('END')
            return self.step_complete_and_stop
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        def _direction_choice(direction_choice_var):
            return direction_choice_var

        action = self.show_choices_message(message_id, ('BAK', _direction_choice, True),
                                           ('FWD', _direction_choice, False)).wait()
        go_back = action.future.result()

        if go_back:
            message_index -= 1
        else:
            message_index += 1

        return self.step_main_loop, message_index
