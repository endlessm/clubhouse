from eosclubhouse.libquest import Quest
import os
import subprocess


class PDFEarthquake(Quest):

    __quest_name__ = 'A Home-grown Earthquake'
    __tags__ = ['pathway:maker']
    __pathway_order__ = 200

    def step_begin(self):
        # @todo
        # this is not the intended final method of displaying this content,
        # ideally this uses another app that has the content ingested
        # in order to prevent bloating the clubhouse flatpak
        self.deploy_file('earthquake_at_home.pdf', 'DOCUMENTS', override=True)
        self.wait_confirm('WELCOME')
        docs_directory = subprocess.check_output(['/usr/bin/xdg-user-dir', 'DOCUMENTS'],
                                                 universal_newlines=True).strip()
        os.system("flatpak-spawn --host evince " + docs_directory + "/earthquake_at_home.pdf")
        return self.step_complete_and_stop
