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
        self.message_id = ''
        return self.step_main_loop()

    def step_main_loop(self):

        if self.message_index > self.__total_messages__:
            return self.step_end

        self.message_id = 'STORY_ADA1_' + str(self.message_index)

        if self.message_index in self.__question_messages__:
            # u"\U0001F44D" for thumbs-up, u"\U0001F44E" for thumbs-down
            choice_pos = (u"\U0001F44D", self.display_answer, True)
            choice_neg = (u"\U0001F44E", self.display_answer, False)
            self.show_choices_message(self.message_id,
                                      choices=[choice_pos, choice_neg],
                                      narrative=True).wait()

        else:
            self.wait_confirm(self.message_id, narrative=True)

        self.message_index += 1
        return self.step_main_loop

    def display_answer(self, answer):
        if answer:
            self.show_confirm_message(self.message_id + '_RPOS', narrative=True).wait()
        else:
            self.show_confirm_message(self.message_id + '_RNEG', narrative=True).wait()

        self.message_index += 1
        return self.step_main_loop

    def step_end(self):
        self.dismiss_message(narrative=True)
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
