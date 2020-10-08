from eosclubhouse.libquest import Quest
from eosclubhouse.system import Hostname, App


class OnboardTour(Quest):

    __tags__ = ['pathway:operating system', 'difficulty:easy']
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 0}
    __pathway_order__ = 1

    def step_begin(self):
        # TODO: Replace with get/set_conf if practical
        self.comp_isfirst = False
        self.os_previous = None
        self.comp_islaptop = Hostname.is_laptop()

        # Apps used
        self.filesApp = App('org.gnome.Nautilus')
        self.softwareApp = App('org.gnome.Software')
        self.settingsApp = App('org.gnome.ControlCenter', is_gtk=False)
        self.officeApp = App('org.libreoffice.LibreOfficeIpc0', is_gtk=False)

        return self.step_greet

    def step_greet(self):
        self.onboarding_overview()
        self.wait_confirm('GREET1')
        # TODO: wait for 'dialog box moved' signal here
        self.wait_confirm('GREET2')
        self.wait_confirm('GREET3')
        firstcomp_action = self.show_choices_message('Q_FIRSTCOMP',
                                                     ('NOQUEST_POSITIVE', None, True),
                                                     ('NOQUEST_NEGATIVE', None, False)).wait()
        self.comp_isfirst = firstcomp_action.future.result()
        if self.comp_isfirst:
            self.wait_confirm('ISFIRSTCOMP')
            return self.step_teachkbm
        else:
            self.wait_confirm('NOTFIRSTCOMP')

        askos_action = self.show_choices_message('Q_PREVOS',
                                                 ('A_PREVIOUS', None, True),
                                                 ('A_FRESH', None, False)).wait()
        if not askos_action.future.result():
            self.wait_confirm('STARTFRESH')
        else:
            self.onboarding_image('onboarding_images\\choose_mac_win.png', size='50% 16:9')
            chooseos_action = self.show_choices_message('Q_WHICHOS',
                                                        ('A_WIN', None, True),
                                                        ('A_MAC', None, False)).wait()
            self.onboarding_clean()
            if chooseos_action.future.result():
                self.os_previous = "win"
                self.wait_confirm('PICKEDWIN')
            else:
                self.os_previous = "mac"
                self.wait_confirm('PICKEDMAC')
        return self.step_desktop

    def step_teachkbm(self):
        self.wait_confirm('KBM1')
        self.wait_confirm('MOUSE1')
        self.wait_confirm('MOUSE2')

        if self.comp_islaptop:
            self.onboarding_image('onboarding_images\\mouse_touchpads.png', size='50% 16:9')
            for msgid in ['MOUSE_LAP1', 'MOUSE_LAP2', 'MOUSE_LAP3']:
                self.wait_confirm(msgid)
            self.onboarding_clean()
        else:
            self.onboarding_image('onboarding_images\\mouse_full.png', size='50% 16:9')
            for msgid in ['MOUSE_DESK1', 'MOUSE_DESK2', 'MOUSE_DESK3']:
                self.wait_confirm(msgid)
            self.onboarding_clean()

        self.wait_confirm('KB1')
        self.onboarding_image('onboarding_images\\kb_ctrl_s.png', size='50% 16:9')
        self.wait_confirm('KB2')
        self.onboarding_clean()
        self.onboarding_image('onboarding_images\\kb_alt_win.png', size='50% 16:9')
        self.wait_confirm('KB3')
        self.onboarding_clean()
        self.wait_confirm('KB4')

        if self.comp_islaptop:
            self.onboarding_image('onboarding_images\\kb_function_fkeys.png', size='50% 16:9')
            self.wait_confirm('KB_LAP1')
            self.wait_confirm('KB_LAP2')
            self.onboarding_clean()
        else:
            self.onboarding_image('onboarding_images\\kb_numlock_states.png', size='50% 16:9')
            self.wait_confirm('KB_DESK')

        self.wait_confirm('KBM_MOVEON')
        return self.step_desktop

    def step_desktop(self):
        self.onboarding_overview()
        self.wait_confirm('DESKTOP_INTRO')

        self.show_highlight_widget('icon-grid')
        self.wait_confirm('DESKTOP_GRID')
        if self.os_previous == 'win':
            self.wait_confirm('DESKTOP_GRID_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('DESKTOP_GRID_MAC')
        self.onboarding_clean()

        self.show_highlight_widget('search-entry')
        self.wait_confirm('DESKTOP_SEARCH')
        if self.os_previous == 'win':
            self.wait_confirm('DESKTOP_SEARCH_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('DESKTOP_SEARCH_MAC')
        self.onboarding_clean()

        self.show_highlight_widget('panel')
        self.wait_confirm('DESKTOP_PANEL')
        if self.os_previous == 'win':
            self.wait_confirm('DESKTOP_PANEL_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('DESKTOP_PANEL_MAC')
        self.onboarding_clean()
        return self.step_apps

    def step_apps(self):
        self.wait_confirm('APPS1')
        self.wait_confirm('APPS2')

        # Wait for user to open App Center
        #   We need to do it this way because g-s is always running,
        #   so we detect foregrounding instead
        self.show_highlight_widget('App Center')
        self.show_hints_message(message_id='APPS3')
        self.wait_for_app_in_foreground(app=self.softwareApp)

        # TODO: clippy highlight Search Box in App Center
        #   self.softwareApp.highlight_object('search_bar')
        self.wait_confirm('APPS4')

        if self.os_previous == 'win':
            self.wait_confirm('APPS4_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('APPS4_MAC')

        if self.has_connection():
            askinstall_action = self.show_choices_message('APPS_Q_HASNET',
                                                          ('APPS_A_YES', None, True),
                                                          ('APPS_A_NO', None, False)).wait()
            if askinstall_action.future.result():
                self.onboarding_clean()
                return self.step_apps_install
            else:
                self.onboarding_clean()
                self.wait_confirm('APPS_NOINSTALL')
        else:
            self.wait_confirm('APPS_NONET')
        return self.step_apps_writer

    def step_apps_install(self):
        self.wait_confirm('APPS_INSTALL1')
        # TODO: clippy highlight Search
        self.wait_confirm('APPS_INSTALL2')
        # TODO: can clippy highlight the download button?
        self.wait_confirm('APPS_INSTALL3')
        self.wait_confirm('APPS_INSTALL4')
        self.wait_confirm('APPS_INSTALL5')
        return self.step_apps_writer

    def step_apps_writer(self):
        self.show_highlight_icon('org.libreoffice.LibreOffice.writer')
        self.show_hints_message(message_id='OPENWRITER')
        self.wait_for_app_launch(app=self.officeApp)
        self.onboarding_clean()

        self.wait_confirm('TYPE')
        # TODO: can we use clippy or some other highlight on the text box itself?
        #       also, this is where we will detect the signal of moving the text box
        self.wait_confirm('TYPE_MOVEBOX')
        # TODO: clippy highlight File -> Save
        self.wait_confirm('FILE')
        # TODO: clippy highlight Save button in Save dialogue
        self.wait_confirm('SAVEDIALOG')
        # TODO: clippy highlight window close (X) button
        self.wait_confirm('CLOSE')

        if self.os_previous == 'win':
            self.wait_confirm('CLOSE_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('CLOSE_MAC')

        self.wait_confirm('APPUSED')
        self.onboarding_clean()
        return self.step_files

    def step_files(self):
        self.onboarding_overview()
        self.show_highlight_widget('Files')
        self.ask_for_app_launch(app=self.filesApp, message_id='FILES_OPENAPP')

        self.wait_confirm('FILES_OPENED')
        if self.os_previous == 'win':
            self.wait_confirm('FILES_TRASH_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('FILES_TRASH_MAC')

        self.wait_confirm('FILES_DOCS')
        self.wait_confirm('FILES_THEREITIS')
        return self.step_saveas

    def step_saveas(self):
        # TODO: wait for LibreOffice open on this dialog
        self.show_hints_message(message_id='FILES_SAVEAS1')
        self.wait_for_app_launch(app=self.officeApp)
        # self.wait_confirm('FILES_SAVEAS1')
        self.wait_confirm('FILES_SAVEAS2')
        # TODO: clippy highlight File -> Save As..
        self.wait_confirm('FILES_SAVEAS3')
        self.wait_confirm('FILES_SAVEAS4')
        self.wait_confirm('FILES_SAVEAS5')
        self.wait_confirm('FILES_SAVEAS6')
        return self.step_search

    def step_search(self):
        self.wait_confirm('SEARCH_INTRO')
        self.onboarding_overview()
        self.show_highlight_widget('search-entry')
        self.wait_confirm('SEARCH_NAME')
        self.onboarding_clean()
        self.show_highlight_widget('searchResults')
        self.wait_confirm('SEARCH_RESULTS')
        self.onboarding_clean()
        self.wait_confirm('SEARCH_MORE')
        if self.has_connection():
            self.wait_confirm('SEARCH_WEB1')
            self.wait_confirm('SEARCH_WEB2')
        return self.step_switchapps

    def step_switchapps(self):
        self.wait_confirm('SWITCHAPPS1')
        self.show_highlight_widget('panel-button endless-button')
        self.wait_confirm('SWITCHAPPS2')
        self.onboarding_clean()
        self.wait_confirm('SWITCHAPPS3')
        self.show_highlight_widget('panelLeft')
        self.wait_confirm('SWITCHAPPS4')
        self.onboarding_clean()
        self.wait_confirm('SWITCHAPPS5')
        return self.step_settings

    def step_settings(self):
        self.wait_confirm('SETTINGS1')

        self.onboarding_overview()
        self.show_highlight_widget('panel')
        self.wait_confirm('SETTINGS_TRAYICONS')
        self.onboarding_clean()

        self.wait_confirm('SETTINGS_MOVEWIN')

        self.show_highlight_widget('panel-status-indicators-box user-mode-indicators-box')
        if self.has_connection():
            self.wait_confirm('SETTINGS_HASNET')
        else:
            self.wait_confirm('SETTINGS_NONET')

        self.wait_confirm('SETTINGS_TRAY_VOL')

        if self.comp_islaptop:
            self.wait_confirm('SETTINGS_LAP_BATT')
        self.wait_confirm('SETTINGS_TRAY_INFO')

        self.show_highlight_widget('panelRight')
        self.wait_confirm('SETTINGS8')

        # TODO: It'd be cool if we could highlight the
        # 'settings' button in the avatar menu here
        self.show_hints_message(message_id='SETTINGS9')
        self.wait_for_app_launch(app=self.settingsApp)
        self.onboarding_clean()

        self.wait_confirm('SETTINGS10')
        # TODO: Can we highlight single/multiple entries
        # in Settings using clippy?
        self.wait_confirm('SETTINGS11')
        # TODO: clippy highlight WiFi
        self.wait_confirm('SETTINGS12')
        # TODO: clippy highlight Background
        self.wait_confirm('SETTINGS13')
        # TODO: clippy highlight Power
        self.wait_confirm('SETTINGS14')

        if self.comp_islaptop:
            self.wait_confirm('SETTINGS_LAP_PWR')
        return self.step_updates

    def step_updates(self):
        self.wait_confirm('UPDATES1')
        self.wait_confirm('UPDATES2')
        self.wait_confirm('UPDATES3')
        self.wait_confirm('UPDATES4')
        # TODO: clippy highlight Automatic Updates
        self.wait_confirm('UPDATES5')
        return self.step_morethings

    def step_morethings(self):
        askmore_action = self.show_choices_message('Q_KNOWMORE',
                                                   ('A_SOMEMORE', None, 'more'),
                                                   ('A_NOMORE', None, 'no')).wait()
        if askmore_action.future.result() == 'more':
            self.wait_confirm("MORE_HACK1")
            self.wait_confirm("MORE_HACK2")
        return self.step_ending

    def step_ending(self):
        self.wait_confirm('ENDING1')
        self.wait_confirm('ENDING3')
        self.wait_confirm('ENDING4')
        self.onboarding_clean()
        self.step_complete_and_stop()

    def step_abort(self):
        self.onboarding_clean()
        super().step_abort()
