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
                self.ask_question(message_id)
            else:
                self.wait_confirm(message_id, narrative=True)
        return self.step_end

    def ask_question(self, proposal_string):
        # u"\U0001F44D"     /    u"\U0001F44E"
        # U+1F44D for thumbs up, U+1F44E for down
        self.show_choices_message(proposal_string, narrative=True, choices=[
            (u"\U0001F44D", self.display_answer, proposal_string, True),
            (u"\U0001F44E", self.display_answer, proposal_string, False)])

    def display_answer(self, proposal_string, answer):
        if answer:
            self.wait_confirm(proposal_string + '_RPOS', narrative=True)
        else:
            self.wait_confirm(proposal_string + '_RNEG', narrative=True)

    def step_end(self):
        self.dismiss_message(narrative=True)
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
