from eosclubhouse.libquest import Quest
import os
import subprocess


class PDFPaperBridge(Quest):

    __quest_name__ = 'Bridge over Papered Water'
    __tags__ = ['mission:faber', 'pathway:maker']
    __mission_order__ = 400

    def step_begin(self):
        # @todo
        # this is not the intended final method of displaying this content,
        # ideally this uses another app that has the content ingested
        # in order to prevent bloating the clubhouse flatpak
        self.deploy_file('paper_to_bridge.pdf', 'DOCUMENTS', override=True)
        self.wait_confirm('WELCOME')
        docs_directory = subprocess.check_output(['/usr/bin/xdg-user-dir', 'DOCUMENTS'],
                                                 universal_newlines=True).strip()
        os.system("flatpak-spawn --host evince " + docs_directory + "/paper_to_bridge.pdf")
        return self.step_complete_and_stop
