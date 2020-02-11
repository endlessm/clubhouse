from eosclubhouse.libquest import Quest, App


class NewCursor(Quest):

    __app_id__ = 'org.glimpse_editor.Glimpse'
    __tags__ = ['pathway:operating system', 'difficulty:hard', 'since:1.6']
    __pathway_order__ = 420

    def setup(self):
        self._app_terminal = App('org.gnome.Terminal')
        self._info_messages = self.get_loop_messages('NEWCURSOR')

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

        self.deploy_file('cursor_template.xmc', '~/Documents/', override=True)
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2')
        self.wait_confirm('GREET3')
        self.wait_confirm('GREET4')
        return self.step_launch

    def step_launch(self):
        self.app.launch()
        # self.app.launch(message_id='LAUNCHGLIMPSE')
        self.wait_confirm('LAUNCHGLIMPSE')
        # self.pause(4)
        # self.wait_for_app_in_foreground(timeout=4)
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Awesome!")
            return self.step_complete_and_stop

        if message_id == self._info_messages[7]:
            self._app_terminal.launch()

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
