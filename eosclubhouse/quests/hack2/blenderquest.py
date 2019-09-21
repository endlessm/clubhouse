from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class BlenderQuest(Quest):

    APP_NAME = 'org.blender.Blender'

    __quest_name__ = '3D Modeling for Beginners'
    __tags__ = ['mission:estelle', 'pathway:art', 'difficulty:medium']
    __mission_order__ = 100
    __pathway_order__ = 100

    def setup(self):
        self._app = App(self.APP_NAME)
        self.NUM_INFO_MESSAGES = 4

    def step_begin(self):
        if not self._app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

        self.wait_confirm('WARN1')
        self.wait_confirm('WARN2')

        action = self.show_choices_message('START_ASK', ('START_YES', None, True),
                                           ('START_NO', None, False)).wait()
        choice = action.future.result()

        if choice:
            self.wait_confirm('LAUNCH')
            self._app.launch()
            self.pause(4)
            return self.step_info_loop
        return self.step_complete_and_stop

    def step_info_loop(self, message_index=1):
        if message_index > self.NUM_INFO_MESSAGES:
            message_index = 1
        elif message_index < 1:
            message_index = self.NUM_INFO_MESSAGES

        message_id = 'INFO_' + str(message_index)

        if message_index == self.NUM_INFO_MESSAGES:
            action = self.show_choices_message(message_id,
                                               ('BAK', None, -1),
                                               ('FWD', None, 1),
                                               ('QUIT', None, 0)).wait()
        else:
            action = self.show_choices_message(message_id,
                                               ('BAK', None, -1),
                                               ('FWD', None, 1)).wait()

        chosen_action = action.future.result()

        if chosen_action == 0:
            self.wait_confirm('BYE')
            return self.step_complete_and_stop
        else:
            message_index += chosen_action
            return self.step_info_loop, message_index
