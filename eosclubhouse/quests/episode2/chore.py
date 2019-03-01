from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound
from eosclubhouse.utils import QS


class Chore(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Chore', 'saniel')
        self._app = App(self.APP_NAME)
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()
        self._ask_question = True

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete('Intro'):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        # @todo: Add steps in between, since the we've waited for the app to be launched but
        # step_end doesn't depend on the app being running.
        return self.step_explanation

    def quiz_choice(self, msg_id, correct):
        self.show_confirm_message(msg_id).wait()
        self._ask_question = not correct

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_confirm_message('EXPLANATION').wait()
        self._ask_question = True
        while (self._ask_question):
            self.show_confirm_message('QUIZ1_QUESTION',
                                      choices=[(QS('{}_QUIZ1_CHOICE1'.format(self._qs_base_id)),
                                                self.quiz_choice, 'QUIZ1_CORRECT', True),
                                               (QS('{}_QUIZ1_CHOICE2'.format(self._qs_base_id)),
                                                self.quiz_choice, 'QUIZ1_INCORRECT', False)]).wait()
        self._ask_question = True
        while (self._ask_question):
            self.show_confirm_message('QUIZ2_QUESTION',
                                      choices=[(QS('{}_QUIZ2_CHOICE2'.format(self._qs_base_id)),
                                                self.quiz_choice, 'QUIZ2_CORRECT', True),
                                               (QS('{}_QUIZ2_CHOICE1'.format(self._qs_base_id)),
                                                self.quiz_choice, 'QUIZ2_INCORRECT', False)]).wait()
        self._ask_question = True
        while (self._ask_question):
            self.show_confirm_message('QUIZ3_QUESTION',
                                      choices=[(QS('{}_QUIZ3_CHOICE1'.format(self._qs_base_id)),
                                                self.quiz_choice, 'QUIZ3_CORRECT', True),
                                               (QS('{}_QUIZ3_CHOICE2'.format(self._qs_base_id)),
                                                self.quiz_choice, 'QUIZ3_INCORRECT', False)]).wait()
        self.show_confirm_message('WRAPUP').wait()
        return self.step_key

    def step_key(self):
        self.show_confirm_message('KEY').wait()
        return self.step_end

    def step_end(self):
        self.give_item('item.key.OperatingSystemApp.2')
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
