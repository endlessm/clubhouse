from eosclubhouse.libquest import Quest


class BootQuest(Quest):

    __app_id__ = 'com.sublimetext.three'
    __tags__ = ['pathway:web', 'difficulty:medium', 'since:1.6']
    __pathway_order__ = 605

    def setup(self):
        self._info_messages = self.get_loop_messages('BOOTQUEST')
        self._component_url_seen = False
        self._codepen_url_seen = False

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Awesome!")
            return self.step_complete_and_stop

        if message_id == self._info_messages[2] and self._component_url_seen is False:
            self.open_url_in_browser('https://getbootstrap.com/docs/4.4/components/')
            self._component_url_seen = True

        if message_id == self._info_messages[4] and self._codepen_url_seen is False:
            self.open_url_in_browser('https://codepen.io/Hack-Computer/pen/ExamVOm')
            self._codepen_url_seen = True

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
