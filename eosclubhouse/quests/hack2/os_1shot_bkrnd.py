from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, App


class OS_Oneshot_Bkrnd(Quest):

    # shoud be terminal
    APP_NAME = 'org.gnome.Terminal'

    __quest_name__ = "OS - Displaying your Prize"
    __tags__ = ['mission:riley', 'pathway:operating system', 'difficulty:hard']
    __mission_order__ = 265
    __pathway_order__ = 265

    TOTAL_MESSAGES = 7
    QUESTION_MESSAGES = []

    def setup(self):
        # shoud be terminal
        self._app = App(self.APP_NAME)
        return self.step_begin

    def step_begin(self):
        # intro dialogue
        self.wait_confirm('1')
        # self._app.launch()
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')

        return self.step_main_loop, 2

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            return self.step_end
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        go_back = False
        is_answer_positive = False

        def _direction_choice(direction_choice_var):
            nonlocal go_back
            go_back = direction_choice_var

        def _yesno_choice(yesno_choice_var):
            nonlocal is_answer_positive
            is_answer_positive = yesno_choice_var

        if message_index in self.QUESTION_MESSAGES:
            self.show_choices_message(message_id,
                                      ('POSITIVE', _yesno_choice, True),
                                      ('NEGATIVE', _yesno_choice, False)).wait()
            suffix = '_RPOS' if is_answer_positive else '_RNEG'
            self.show_confirm_message(message_id + suffix).wait()
            message_index = message_index + 1

        else:
            self.show_choices_message(message_id, ('BAK', _direction_choice, True),
                                      ('FWD', _direction_choice, False)).wait()
            if go_back:
                message_index = message_index - 1
            else:
                message_index = message_index + 1

        return self.step_main_loop, message_index

    def step_end(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
