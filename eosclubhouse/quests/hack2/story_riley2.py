from eosclubhouse.libquest import Quest


class Story_Riley2(Quest):

    __tags__ = ['pathway:web', 'skillset:Narrative', 'difficulty:easy',
                'skillset:LaunchQuests', 'skillset:felix']
    __pathway_order__ = 55
    __is_narrative__ = True

    QUESTION_MESSAGES = []

    def setup(self):
        self._info_messages = self.get_loop_messages('STORY_RILEY2')

    def step_begin(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id in self.QUESTION_MESSAGES:
            action = self.show_choices_message(message_id,
                                               ('NOQUEST_POSITIVE', None, True),
                                               ('NOQUEST_NEGATIVE', None, False),
                                               narrative=True).wait()
            suffix = '_RPOS' if action.future.result() else '_RNEG'
            self.show_confirm_message(message_id + suffix, narrative=True).wait()

        else:
            self.wait_confirm(message_id, narrative=True)

        if message_id == self._info_messages[-1]:
            return self.step_complete_and_stop

        return self.step_begin, message_index + 1

    def step_complete_and_stop(self):
        self.dismiss_message(narrative=True)
        super().step_complete_and_stop()
