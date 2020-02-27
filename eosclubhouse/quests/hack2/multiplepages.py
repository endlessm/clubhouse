from eosclubhouse.libquest import Quest


class MultiplePages(Quest):

    __app_id__ = 'com.sublimetext.three'
    __tags__ = ['pathway:web', 'difficulty:medium', 'since:1.8']
    __pathway_order__ = 615

    def setup(self):
        self._info_messages = self.get_loop_messages('MULTIPLEPAGES', start=3)

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

        self.wait_confirm('1')
        self.wait_confirm('2')
        self.deploy_file('MultiplePages/images/dog.jpeg',
                         '~/Documents/multiplepages/images/', override=True)
        self.deploy_file('MultiplePages/images/camera.jpeg',
                         '~/Documents/multiplepages/images/', override=True)
        self.deploy_file('MultiplePages/images/balloon.jpeg',
                         '~/Documents/multiplepages/images/', override=True)
        self.deploy_file('MultiplePages/images/email.jpeg',
                         '~/Documents/multiplepages/images/', override=True)
        self.deploy_file('MultiplePages/images/family.jpeg',
                         '~/Documents/multiplepages/images/', override=True)
        self.deploy_file('MultiplePages/images/tugowar.jpeg',
                         '~/Documents/multiplepages/images/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap.css',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap.css.map',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap.min.css',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap.min.css.map',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-grid.css',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-grid.css.map',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-grid.min.css',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-grid.min.css.map',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-reboot.css',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-reboot.css.map',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-reboot.min.css',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/css/bootstrap-reboot.min.css.map',
                         '~/Documents/multiplepages/css/', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.bundle.js',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.bundle.js.map',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.bundle.min.js',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.bundle.min.js.map',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.js',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.js.map',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.min.js',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/bootstrap.min.js.map',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/js/jquery-3.4.1.min.js',
                         '~/Documents/multiplepages/js', override=True)
        self.deploy_file('MultiplePages/index.html',
                         '~/Documents/multiplepages', override=True)
        self.deploy_file('MultiplePages/contact.html',
                         '~/Documents/multiplepages', override=True)
        self.deploy_file('MultiplePages/favs.html',
                         '~/Documents/multiplepages', override=True)
        self.deploy_file('MultiplePages/about.html',
                         '~/Documents/multiplepages', override=True)
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Sweet!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
