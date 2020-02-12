from eosclubhouse.libquest import Quest


class BlendPerson3(Quest):

    __tags__ = ['pathway:art', 'difficulty:medium', 'since:1.6']
    __pathway_order__ = 637

    def setup(self):
        self._info_messages = self.get_loop_messages('BLENDPERSON3')

    def step_begin(self):
        self.deploy_file('BlendPerson/low-poly-character.blend',
                         '~/BlenderSources/LowPolyPerson', override=True)
        self.deploy_file('BlendPerson/low-poly-character-rigged-complete.blend',
                         '~/BlenderSources/LowPolyPerson', override=True)
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Thanks, bye!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
