from eosclubhouse.libquest import Quest
import os


class PDFEarthquake(Quest):

    __quest_name__ = 'A Home-grown Earthquake'
    __tags__ = ['mission:faber', 'pathway:maker']
    __mission_order__ = 200

    def step_begin(self):
        self.deploy_file('earthquake_at_home.pdf', '~/Documents/', override=True)
        self.wait_confirm('WELCOME')
        os.system("flatpak-spawn --host evince ~/Documents/earthquake_at_home.pdf")
        return self.step_complete_and_stop
