from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Story_Ada1(Quest):

    __quest_name__ = 'Checking in with Ada'
    __tags__ = ['mission:ada']
    __mission_order__ = 50
    __question_steps__ = [2, 22]
    __total_steps__ = 27

    def step_begin(self):
        return self.step_main_loop

    def step_main_loop(self):
        # cycle through the steps
        # for each step check
        # is it a question step?
        #   ask the question, continue
        # is it the last step?
        #   goto end
        #
        for step in range(1, self.__total_steps__ + 1):
            message_id = 'STORY_ADA1_' + str(step)
            if step in self.__question_steps__:
                # self.ask_question(message_id)
                # u"\U0001F44D" for thumbs-up, u"\U0001F44E" for thumbs-down
                choice_pos = (u"\U0001F44D", self.display_answer, message_id, True)
                choice_neg = (u"\U0001F44E", self.display_answer, message_id, False)
                self.show_choices_message(message_id, narrative=True,
                                          choices=[choice_pos, choice_neg]).wait()
            else:
                self.wait_confirm(message_id, narrative=True)
        return self.step_end

    # def ask_question(self, message_id):
    #     # u"\U0001F44D" for thumbs-up, u"\U0001F44E" for thumbs-down
    #     self.show_choices_message(message_id, narrative=True, choices=[
    #         (u"\U0001F44D", self.display_answer, message_id, True),
    #         (u"\U0001F44E", self.display_answer, message_id, False)]).wait()

    def display_answer(self, message_id, answer):
        if answer:
            self.wait_confirm(message_id + '_RPOS', narrative=True)
        else:
            self.wait_confirm(message_id + '_RNEG', narrative=True)

    def step_end(self):
        self.dismiss_message(narrative=True)
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
