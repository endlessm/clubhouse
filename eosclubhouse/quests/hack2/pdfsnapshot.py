from eosclubhouse.libquest import Quest
import os
import subprocess


class PDFSnapshot(Quest):

    __quest_name__ = "Let's be (Photo) realistic"
    __tags__ = ['mission:estelle', 'pathway:art']
    __mission_order__ = 400

    def step_begin(self):
        # @todo
        # this is not the intended final method of displaying this content,
        # ideally this uses another app that has the content ingested
        # in order to prevent bloating the clubhouse flatpak
        self.deploy_file('snapshot.pdf', 'DOCUMENTS', override=True)
        self.wait_confirm('WELCOME')
        docs_directory = subprocess.check_output(['/usr/bin/xdg-user-dir', 'DOCUMENTS'],
                                                 universal_newlines=True).strip()
        os.system("flatpak-spawn --host evince " + docs_directory + "/snapshot.pdf")
        return self.step_complete_and_stop
