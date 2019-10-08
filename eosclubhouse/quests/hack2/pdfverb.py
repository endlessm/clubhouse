from eosclubhouse.libquest import Quest
import os
import subprocess


class PDFVerb(Quest):

    __quest_name__ = 'A Verb in the Hat is worth...'
    __tags__ = ['mission:faber', 'pathway:maker']
    __mission_order__ = 500

    def step_begin(self):
        # @todo
        # this is not the intended final method of displaying this content,
        # ideally this uses another app that has the content ingested
        # in order to prevent bloating the clubhouse flatpak
        self.deploy_file('verb_in_a_hat.pdf', 'DOCUMENTS', override=True)
        self.wait_confirm('WELCOME')
        docs_directory = subprocess.check_output(['/usr/bin/xdg-user-dir', 'DOCUMENTS'],
                                                 universal_newlines=True).strip()
        os.system("flatpak-spawn --host evince " + docs_directory + "/verb_in_a_hat.pdf")
        return self.step_complete_and_stop
