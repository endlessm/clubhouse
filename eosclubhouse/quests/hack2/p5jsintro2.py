from eosclubhouse.libquest import Quest
import os


class P5JSIntro2(Quest):

    __tags__ = ['pathway:web', 'difficulty:medum']
    __pathway_order__ = 552

    def setup(self):
        self._info_messages = self.get_loop_messages('P5JSINTRO2', start=3)

    def step_begin(self):
        self.wait_confirm('1')
        self.wait_confirm('2')
        return self.step_launch

    def step_launch(self):
        os.system('xdg-open https://editor.p5js.org/')
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label='See you soon!')
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
