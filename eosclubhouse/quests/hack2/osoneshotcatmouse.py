from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class OSOneshotCatMouse(Quest):

    APP_NAME = 'org.gnome.Terminal'

    __tags__ = ['pathway:operating system', 'difficulty:hard',
                'skillset:LaunchQuests', 'skillset:felix']
    __pathway_order__ = 250

    TOTAL_MESSAGES = 56

    def setup(self):
        self._app = App(self.APP_NAME)
        return self.step_begin

    def step_begin(self):
        self.deploy_file('mouse', '~/yarnbasket/blueyarn/', override=True)
        self.deploy_file('yarn_bits', '~/yarnbasket/greenyarn/', override=True)
        self.deploy_file('yarn_bits', '~/yarnbasket/redyarn/', override=True)
        # intro dialogue
        for index in range(1, 7):
            self.wait_confirm(str(index))
        # launch the terminal for the user, makes it easier - this is the first quest
        self._app.launch()
        self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_main_loop, 7

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            self.wait_confirm('END')
            return self.step_complete_and_stop
        elif message_index < 1:
            message_index = 1

        if message_index == 48:
            self.deploy_file('maybe_a_mouse', '~/yarnbasket/greenyarn/', override=True)
        if message_index == 52:
            self.deploy_file('actually_a_mouse', '~/yarnbasket/redyarn/', override=True)

        message_id = str(message_index)

        action = self.show_choices_message(message_id, ('NOQUEST_NAV_BAK', None, -1),
                                           ('NOQUEST_NAV_FWD', None, 1)).wait()
        message_index += action.future.result()

        return self.step_main_loop, message_index
