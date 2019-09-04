from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, App


class OSOneshotFollow(Quest):

    APP_NAME = 'org.gnome.Terminal'

    __quest_name__ = "The Terminal - 3 - On the Trail"
    __tags__ = ['mission:riley', 'pathway:operating system', 'difficulty:hard']
    __mission_order__ = 260
    __pathway_order__ = 260

    TOTAL_MESSAGES = 12

    def setup(self):
        self._app = App(self.APP_NAME)
        return self.step_begin

    def step_begin(self):
        self.wait_confirm('1')
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')

        return self.step_main_loop, 2

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            return self.step_end
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        def _direction_choice(direction_choice_var):
            return direction_choice_var

        action = self.show_choices_message(message_id, ('BAK', _direction_choice, True),
                                           ('FWD', _direction_choice, False)).wait()
        go_back = action.future.result()

        if go_back:
            message_index -= 1
        else:
            message_index += 1

        return self.step_main_loop, message_index

    def step_end(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
