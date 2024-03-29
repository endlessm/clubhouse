from eosclubhouse.libquest import Quest


class KritaPixel(Quest):

    __app_id__ = 'org.kde.krita'
    __app_common_install_name__ = 'KRITA'
    __tags__ = ['pathway:art', 'difficulty:medium', 'since:2.0']
    __pathway_order__ = 653

    def setup(self):
        self._info_messages = self.get_loop_messages('KRITAPIXEL', start=2)

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
