from eosclubhouse.libquest import Quest


class OSAdventure(Quest):

    __app_id__ = 'org.gnome.Terminal'
    __tags__ = ['pathway:operating system', 'difficulty:medium', 'since:1.4']
    __pathway_order__ = 410

    def setup(self):
        self._info_messages = self.get_loop_messages('OSADVENTURE')

    def step_begin(self):
        self.wait_confirm('GREET')
        return self.step_launch

    def step_launch(self):
        self.ask_for_app_launch(message_id='LAUNCH')
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Awesome!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
