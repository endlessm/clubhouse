from eosclubhouse.libquest import Quest
from eosclubhouse.system import Tour
from eosclubhouse.network import NetworkManager


class TestQuest(Quest):

    __tags__ = ['pathway:operating system']
    __pathway_order__ = 1

    def step_begin(self):
        # self.wait_for_highlight_icon('org.libreoffice.LibreOffice', text='Click Here!')
        # self.wait_for_highlight_fuzzy(position='center', size='30%')
        # self.deploy_file('test_image.png', '~/', override=True)
        # Tour.show_image('~/test_image.jpg', '50% 16:9')
        # Tour.clean()
        self.wait_confirm('NOQUEST_SUBTITLE')
        self.wait_confirm('NOQUEST_DESCRIPTION')
        if NetworkManager.is_connected():
            self.wait_confirm('TOURTEST_SETTINGS_HASNET')
        else:
            self.wait_confirm('TOURTEST_SETTINGS_NONET')
        return self.step_complete_and_stop
