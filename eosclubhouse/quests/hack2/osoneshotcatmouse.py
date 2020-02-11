from eosclubhouse.libquest import Quest


class OSOneshotCatMouse(Quest):

    __app_id__ = 'org.gnome.Terminal'
    __tags__ = ['pathway:operating system', 'difficulty:hard',
                'skillset:LaunchQuests', 'skillset:felix']
    __pathway_order__ = 250

    def setup(self):
        self._info_messages = self.get_loop_messages('OSONESHOTCATMOUSE', start=7)

    def step_begin(self):
        self.deploy_file('mouse', '~/yarnbasket/blueyarn/', override=True)
        self.deploy_file('yarn_bits', '~/yarnbasket/greenyarn/', override=True)
        self.deploy_file('yarn_bits', '~/yarnbasket/redyarn/', override=True)
        # intro dialogue
        for index in range(1, 7):
            self.wait_confirm(str(index))
        # launch the terminal for the user, makes it easier - this is the first quest
        self.app.launch()
        self.wait_for_app_launch()

        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label='See you around!')
            return self.step_complete_and_stop
        elif message_id == 'OSONESHOTCATMOUSE_45':
            self.deploy_file('maybe_a_mouse', '~/yarnbasket/greenyarn/', override=True)
        elif message_id == 'OSONESHOTCATMOUSE_50':
            self.deploy_file('actually_a_mouse', '~/yarnbasket/redyarn/', override=True)

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
