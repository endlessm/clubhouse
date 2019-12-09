from eosclubhouse.libquest import Quest
from gi.repository import Gio


class RPiWebCard(Quest):

    __tags__ = ['pathway:web', 'difficulty:medium']
    __pathway_order__ = 590

    def step_begin(self):
        self.wait_confirm('WELCOME')
        Gio.AppInfo.launch_default_for_uri_async(
            'https://projects.raspberrypi.org/en/projects/happy-birthday/7')
        self.wait_confirm('LINK')
        self.wait_confirm('BYE', confirm_label='Later!')
        return self.step_complete_and_stop
