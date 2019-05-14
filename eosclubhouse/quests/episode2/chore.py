import random

from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Chore(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Chore', 'saniel')
        self._app = App(self.APP_NAME)
        self._ask_question = True

    def step_begin(self):
        self.ask_for_app_launch(self._app)

        # @todo: Add steps in between, since the we've waited for the app to be launched but
        # step_end doesn't depend on the app being running.
        return self.step_explanation

    def show_quiz_question(self, quiz_id, *choices):
        is_correct = False
        answers = []

        def _quiz_choice(is_correct_choice):
            nonlocal is_correct
            is_correct = is_correct_choice

        # We want the choices's order to appear randomly on every run, so it makes the quizz more
        # interesting.
        random_choices = random.sample(choices, k=len(choices))

        for choice_msg_id, is_correct_choice in random_choices:
            answers.append((choice_msg_id, _quiz_choice, is_correct_choice))

        while not self.is_cancelled():
            quiz_question_id = '{}_QUESTION'.format(quiz_id)
            self.show_choices_message(quiz_question_id, *answers).wait()

            if self.is_cancelled():
                return

            if is_correct:
                self.show_confirm_message('{}_CORRECT'.format(quiz_id)).wait()
                break
            else:
                self.show_confirm_message('{}_INCORRECT'.format(quiz_id)).wait()

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_confirm_message('EXPLANATION').wait()

        self.show_quiz_question('QUIZ1', ('QUIZ1_CHOICE1', True), ('QUIZ1_CHOICE2', False))

        self.show_quiz_question('QUIZ2', ('QUIZ2_CHOICE1', False), ('QUIZ2_CHOICE2', True))

        self.show_quiz_question('QUIZ3', ('QUIZ3_CHOICE1', True), ('QUIZ3_CHOICE2', False))

        self.show_confirm_message('WRAPUP').wait()
        return self.step_key

    def step_key(self):
        self.show_confirm_message('KEY').wait()
        return self.step_end

    def step_end(self):
        self.give_item('item.key.OperatingSystemApp.2')
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
