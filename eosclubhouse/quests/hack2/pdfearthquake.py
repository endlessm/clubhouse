from eosclubhouse.libquest import Quest
import os


class PDFEarthquake(Quest):

    __quest_name__ = 'A Home-grown Earthquake'
    __tags__ = ['mission:faber', 'pathway:maker']
    __mission_order__ = 200

    def step_begin(self):
        self.deploy_file('earthquake.pdf', '~/', override=True)
        self.wait_confirm('WELCOME')
        os.system("flatpak-spawn --host evince ~/earthquake.pdf")
        return self.step_complete_and_stop
