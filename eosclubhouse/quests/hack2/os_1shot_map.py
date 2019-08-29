from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, App


class OS_Oneshot_Map(Quest):

    # shoud be terminal
    APP_NAME = 'org.gnome.Terminal'

    __quest_name__ = "OS - Grep... Is that a fruit?"
    __tags__ = ['mission:riley', 'pathway:operating system', 'difficulty:hard']
    __mission_order__ = 255
    __pathway_order__ = 255

    TOTAL_MESSAGES = 17

    def setup(self):
        # shoud be terminal
        self._app = App(self.APP_NAME)
        return self.step_begin

    def step_begin(self):
        # intro dialogue
        self.wait_confirm('1')
        self.wait_confirm('2')
        # launch the terminal for the user, makes it easier
        # this DOES assume the Terminal is not already launched
        # self._app.launch()
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')

        return self.step_main_loop, 3

    def step_main_loop(self, message_index):
        # TODO
        # get messageid
        # propose question with message id
        # pos? increment
        # neg? decrement
        # da capo

        if message_index > self.TOTAL_MESSAGES:
            return self.step_end
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        go_back = False

        def _direction_choice(direction_choice_var):
            nonlocal go_back
            go_back = direction_choice_var

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
