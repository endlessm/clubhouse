from eosclubhouse.libquest import Quest
import os


class MakerPDF(Quest):

    __quest_name__ = 'Home-grown Earthquake'
    __tags__ = ['mission:faber', 'pathway:maker', 'difficulty:medium']
    __mission_order__ = 200

    def step_begin(self):
        self.deploy_file('earthquake.pdf', '~/', override=True)
        self.wait_confirm('WELCOME')
        os.system('gio open earthquake.pdf')
        return self.step_complete_and_stop
