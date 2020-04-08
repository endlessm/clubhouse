from eosclubhouse.libquest import Quest


class BlenderQuest(Quest):

    __app_id__ = 'org.blender.Blender'
    __tags__ = ['pathway:maker', 'difficulty:hard', 'skillset:LaunchQuests']
    __pathway_order__ = 100

    def setup(self):
        self._info_messages = self.get_loop_messages('INFO')

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

        self.wait_confirm('WARN1')
        self.wait_confirm('WARN2')

        action = self.show_choices_message('START_ASK', ('START_YES', None, True),
                                           ('START_NO', None, False)).wait()

        if action.future.result():
            self.wait_confirm('LAUNCH')
            self.app.launch()
            self.pause(4)
            return self.step_info_loop
        return self.step_abort

    def step_info_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        options = [
            ('NOQUEST_NAV_BAK', None, -1),
            ('NOQUEST_NAV_FWD', None, 1),
        ]

        if message_id == self._info_messages[-1]:
            options.append(('QUIT', None, 0))

        action = self.show_choices_message(message_id, *options).wait()

        chosen_action = action.future.result()

        if chosen_action == 0:
            self.wait_confirm('BYE', confirm_label='See you later!')
            return self.step_complete_and_stop
        else:
            return self.step_info_loop, message_index + chosen_action
