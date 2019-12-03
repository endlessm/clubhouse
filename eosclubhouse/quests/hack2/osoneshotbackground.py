from eosclubhouse.libquest import Quest


class OSOneshotBackground(Quest):

    __app_id__ = 'org.gnome.Terminal'
    __tags__ = ['pathway:operating system', 'difficulty:hard', 'skillset:LaunchQuests']
    __pathway_order__ = 265

    def setup(self):
        self._info_messages = self.get_loop_messages('OSONESHOTBACKGROUND', start=2)

    def step_begin(self):
        self.deploy_file('treasure.jpg',
                         '~/yarnbasket/thereisaworl/doutsi/detheac/ademyyou/rfrien/dshave/secrets',
                         override=True)
        self.wait_confirm('1')
        self.ask_for_app_launch()

        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label='Looking forward to it!')
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
