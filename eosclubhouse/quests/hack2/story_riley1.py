from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Story_Riley1(Quest):

    __quest_name__ = 'The Life of Riley - Part 1'
    __tags__ = ['mission:ada']  # riley not set up yet
    __mission_order__ = 52      # 50 when applied to riley
    __is_narrative__ = True

    QUESTION_MESSAGES = [7]
    TOTAL_MESSAGES = 26

    def step_begin(self):
        return self.step_main_loop, 1

    def step_main_loop(self, message_index):

        if message_index > self.TOTAL_MESSAGES:
            return self.step_end

        message_id = str(message_index)

        is_answer_positive = False

        def _answer_choice(user_answer):
            nonlocal is_answer_positive
            is_answer_positive = user_answer

        if message_index in self.QUESTION_MESSAGES:
            self.show_choices_message(message_id,
                                      ('POSITIVE', _answer_choice, True),
                                      ('NEGATIVE', _answer_choice, False),
                                      narrative=True).wait()
            suffix = '_RPOS' if is_answer_positive else '_RNEG'
            self.show_confirm_message(message_id + suffix, narrative=True).wait()

        else:
            self.wait_confirm(message_id, narrative=True)

        return self.step_main_loop, message_index + 1

    def step_end(self):
        self.dismiss_message(narrative=True)
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
