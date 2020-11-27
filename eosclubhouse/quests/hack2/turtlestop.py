from eosclubhouse.libquest import Quest


class TurtleStop(Quest):

    __app_id__ = 'org.laptop.TurtleArtActivity'
    __app_common_install_name__ = 'TURTLEBLOCKS'
    __tags__ = ['pathway:operating system', 'difficulty:easy', 'since:2.0']
    __pathway_order__ = 660

    def setup(self):
        self._info_messages = self.get_loop_messages('TURTLESTOP', start=2)

    def step_begin(self):
        return self.step_launch

    def step_launch(self):
        self.wait_confirm('1')
        if self.is_cancelled():
            return self.step_abort()
        self.app.launch()
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="You bet!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
