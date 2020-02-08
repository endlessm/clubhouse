from eosclubhouse.libquest import Quest


class BlendPerson1(Quest):

    __app_id__ = 'org.blender.Blender'
    __tags__ = ['pathway:art', 'difficulty:medium', 'since:1.6']
    __pathway_order__ = 635

    def setup(self):
        self._info_messages = self.get_loop_messages('BLENDPERSON1')

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOQUEST_BLENDER_NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort
        self.wait_confirm('GREET')
        if self.is_cancelled():
            return self.step_abort()
        return self.step_launch

    def step_launch(self):
        self.deploy_file('BlendPerson/reference-sheet.png',
                         '~/BlenderSources/LowPolyPerson', override=True)
        self.open_url_in_browser('https://www.youtube.com/watch?v=4OUYOKGl7x0')
        self.app.launch()
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="See you next time!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
