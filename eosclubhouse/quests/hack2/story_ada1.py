from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Story_Ada1(Quest):

    __quest_name__ = 'Checking in with Ada'
    __tags__ = ['mission:ada']
    __mission_order__ = 50
    __question_messages__ = [2, 22]
    __total_messages__ = 27

    def step_begin(self):
        self.message_index = 1
        return self.step_main_loop

    def step_main_loop(self):

        if self.message_index > self.__total_messages__:
            return self.step_end

        is_answer_positive = False

        def _answer_choice(user_answer):
            nonlocal is_answer_positive
            is_answer_positive = user_answer

        message_id = 'STORY_ADA1_' + str(self.message_index)

        if self.message_index in self.__question_messages__:

            self.show_choices_message(message_id,
                                      ('YES', _answer_choice, True),
                                      ('NO', _answer_choice, False),
                                      narrative=True).wait()

            suffix = '_RPOS' if is_answer_positive else '_RNEG'
            self.show_confirm_message(message_id + suffix, narrative=True).wait()

        else:
            self.wait_confirm(message_id, narrative=True)

        self.message_index += 1
        return self.step_main_loop

    def step_end(self):
        self.dismiss_message(narrative=True)
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
