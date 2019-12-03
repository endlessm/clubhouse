from eosclubhouse.libquest import Quest


class WobblyBash(Quest):

    __app_id__ = 'org.gnome.Terminal'
    __tags__ = ['pathway:operating system', 'difficulty:hard']
    __pathway_order__ = 400

    def setup(self):
        self._info_messages = self.get_loop_messages('WOBBLYBASH', start=3)

    def step_begin(self):
        self.wait_confirm('1')
        # gsettings reset org.gnome.shell wobbly-effect
        # gsettings reset org.gnome.shell wobbly-object-movement-range
        # gsettings reset org.gnome.shell wobbly-slowdown-factor
        # gsettings reset org.gnome.shell wobbly-spring-friction
        # gsettings reset org.gnome.shell wobbly-spring-k
        return self.step_launch

    def step_launch(self):
        self.ask_for_app_launch(message_id='2')
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Can't wait!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
