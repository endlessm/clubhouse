from eosclubhouse.libquest import Quest


class BlendMonster5(Quest):

    __app_id__ = 'org.blender.Blender'
    __tags__ = ['pathway:maker', 'difficulty:hard']
    __pathway_order__ = 604

    def setup(self):
        self._info_messages = self.get_loop_messages('INFO', start=1)

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

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
