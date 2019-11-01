from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class OSOneshotBackground(Quest):

    APP_NAME = 'org.gnome.Terminal'

    __tags__ = ['pathway:operating system', 'difficulty:hard', 'skillset:LaunchQuests']
    __pathway_order__ = 265

    TOTAL_MESSAGES = 10

    def setup(self):
        self._app = App(self.APP_NAME)
        return self.step_begin

    def step_begin(self):
        self.deploy_file('treasure.jpg',
                         '~/yarnbasket/thereisaworl/doutsi/detheac/ademyyou/rfrien/dshave/secrets',
                         override=True)
        self.wait_confirm('1')
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')

        return self.step_main_loop, 2

    def step_main_loop(self, message_index):
        if message_index > self.TOTAL_MESSAGES:
            self.wait_confirm('END')
            return self.step_complete_and_stop
        elif message_index < 1:
            message_index = 1

        message_id = str(message_index)

        action = self.show_choices_message(message_id, ('NOQUEST_NAV_BAK', None, -1),
                                           ('NOQUEST_NAV_FWD', None, 1)).wait()
        message_index += action.future.result()

        return self.step_main_loop, message_index
