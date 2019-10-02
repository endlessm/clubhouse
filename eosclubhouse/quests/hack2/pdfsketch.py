from eosclubhouse.libquest import Quest
import os
import subprocess


class PDFSketch(Quest):

    __quest_name__ = 'A Sketchy Proposition'
    __tags__ = ['mission:faber', 'pathway:maker']
    __mission_order__ = 300

    def step_begin(self):
        # @todo
        # this is not the intended final method of displaying this content,
        # ideally this uses another app that has the content ingested
        # in order to prevent bloating the clubhouse flatpak
        self.deploy_file('sketch_prototype.pdf', 'DOCUMENTS', override=True)
        self.wait_confirm('WELCOME')
        docs_directory = subprocess.check_output(['/usr/bin/xdg-user-dir', 'DOCUMENTS'],
                                                 universal_newlines=True).strip()
        os.system("flatpak-spawn --host evince " + docs_directory + "/sketch_prototype.pdf")
        return self.step_complete_and_stop
