from eosclubhouse.libquest import Quest


class DomQuest(Quest):

    __tags__ = ['pathway:web', 'difficulty:medium', 'since:1.4']
    __pathway_order__ = 600

    def setup(self):
        self._info_messages = self.get_loop_messages('DOMQUEST', start=3)

    def step_begin(self):
        self.wait_confirm('1')
        self.wait_confirm('2')
        return self.step_launch

    def step_launch(self):
        self.open_url_in_browser(
            'https://codepen.io/Hack-Computer/pen/WNbpOjV')
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Awesome!")
            return self.step_complete_and_stop

        if message_id == self._info_messages[3]:
            self.open_url_in_browser('http://unsplash.com')

        if message_id == self._info_messages[11]:
            self.open_url_in_browser('http://bit.ly/maphackdom')

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
