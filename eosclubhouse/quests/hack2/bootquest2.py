from eosclubhouse.libquest import Quest


class BootQuest2(Quest):

    __app_id__ = 'org.gnome.Terminal'
    __tags__ = ['pathway:web', 'difficulty:medium', 'since:1.5']
    __pathway_order__ = 615

    def setup(self):
        self._info_messages = self.get_loop_messages('BOOTQUEST2', start=3)

    def step_begin(self):
        self.wait_confirm('1')
        self.wait_confirm('2')
        return self.step_launch

    def step_launch(self):
        self.app.launch()
        self.wait_for_app_launch()
        return self.step_main_loop

    def step_main_loop(self, message_index=3):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Sweet!")
            return self.step_complete_and_stop

        if message_id == self._info_messages[6]:
            self.open_url_in_browser('https://getbootstrap.com/docs/4.4/getting-started/download/')

        if message_id == self._info_messages[10]:
            self.open_url_in_browser('https://code.jquery.com/jquery-3.4.1.min.js')

        if message_id == self._info_messages[14]:
            self.open_url_in_browser('https://getbootstrap.com/docs/4.4/getting-started/introduction')  # noqa: E501

        if message_id == self._info_messages[18]:
            self.open_url_in_browser('https://getbootstrap.com/docs/4.4/components/carousel/')

        if message_id == self._info_messages[22]:
            self.deploy_file('dog.jpg', '~/Documents/myproject/images', override=True)
            self.deploy_file('cats.jpg', '~/Documents/myproject/images', override=True)
            self.deploy_file('bird.jpg', '~/Documents/myproject/images', override=True)

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
