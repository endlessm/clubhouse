from eosclubhouse.libquest import Quest
from eosclubhouse.system import Hostname


class OnboardTour(Quest):

    __tags__ = ['pathway:operating system']
    # TODO: Make sure this line is uncommented when shipping!
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 0}
    __pathway_order__ = 1

    # TODO: Replace this with get/set_conf if possible
    comp_isfirst = False
    comp_islaptop = False
    comp_screenx = 1920
    comp_screeny = 1080
    os_previous = None

    # TODO: Make sure this function is uncommented when shipping!
    def setup(self):
        self.auto_offer = True
        self.skippable = True

    def step_begin(self):
        self.comp_islaptop = Hostname.is_laptop()
        return self.step_greet

    def step_greet(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2')
        self.wait_confirm('GREET3')
        firstcomp_action = self.show_choices_message('Q_FIRSTCOMP', ('NOQUEST_POSITIVE', None, True), # noqa E501
                         ('NOQUEST_NEGATIVE', None, False)).wait() # noqa E501
        self.comp_isfirst = firstcomp_action.future.result()
        if self.comp_isfirst:
            self.wait_confirm('ISFIRSTCOMP')
            return self.step_teachkbm
        else:
            self.wait_confirm('NOTFIRSTCOMP')

        askos_action = self.show_choices_message('Q_WHICHOS', ('A_WIN', None, True),
                     ('A_MAC', None, False)).wait() # noqa E501
        if not askos_action.future.result():
            self.wait_confirm('STARTFRESH')
        else:
            self.onboarding_image('temp_mac_win.png', size='50% 16:9')
            chooseos_action = self.show_choices_message('Q_WHICHOS', ('A_WIN', None, True),
                            ('A_MAC', None, False)).wait() # noqa E501
            self.onboarding_clean()
            if chooseos_action.future.result():
                self.os_previous = "win"
                self.wait_confirm('PICKEDWIN')
            else:
                self.os_previous = "mac"
                self.wait_confirm('PICKEDMAC')
        return self.step_desktop

    def step_teachkbm(self):
        # TODO: Need images for this section to reduce text
        self.wait_confirm('KBM1')
        self.wait_confirm('MOUSE1')
        self.wait_confirm('MOUSE2')

        if self.comp_islaptop:
            self.onboarding_image('temp_touchpads.png', size='50% 16:9')
            for msgid in ['MOUSE_LAP1', 'MOUSE_LAP2', 'MOUSE_LAP3']:
                self.wait_confirm(msgid)
            self.onboarding_clean()
        else:
            self.onboarding_image('temp_mouse_full.png', size='50% 16:9')
            for msgid in ['MOUSE_DESK1', 'MOUSE_DESK2', 'MOUSE_DESK3']:
                self.wait_confirm(msgid)
            self.onboarding_clean()

        self.wait_confirm('KB1')
        self.wait_confirm('KB2')
        self.wait_confirm('KB3')
        self.wait_confirm('KB4')

        if self.comp_islaptop:
            self.onboarding_image('temp_function_and_fkeys.png', size='50% 16:9')
            self.wait_confirm('KB_LAP1')
            self.wait_confirm('KB_LAP2')
            self.onboarding_clean()
        else:
            self.wait_confirm('KB_DESK')

        self.wait_confirm('KBM_MOVEON')
        return self.step_desktop

    def step_desktop(self):
        self.show_highlight_fuzzy('center', '75%')
        self.wait_confirm('DESKTOP1')
        self.onboarding_clean()
        self.show_highlight_widget('icon-grid')
        self.wait_confirm('DESKTOP2')
        self.onboarding_clean()

        if self.os_previous == 'win':
            self.wait_confirm('DESKTOP_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('DESKTOP_MAC')

        self.show_highlight_widget('Files')
        self.wait_confirm('DOCS')
        self.onboarding_clean()

        if self.os_previous == 'win':
            self.show_highlight_widget('search-entry')
            self.wait_confirm('STARTMENU1')
            self.onboarding_clean()
            self.show_highlight_widget('App Center')
            self.wait_confirm('STARTMENU2')
            self.onboarding_clean()
            self.show_highlight_widget('Files')
            self.wait_confirm('TRASH_WIN')
            self.onboarding_clean()
        if self.os_previous == 'mac':
            self.show_highlight_widget('search-entry')
            self.wait_confirm('SPOTLIGHT1')
            self.onboarding_clean()
            self.show_highlight_widget('App Center')
            self.wait_confirm('SPOTLIGHT2')
            self.onboarding_clean()
            self.show_highlight_widget('Files')
            self.wait_confirm('TRASH_MAC')
            self.onboarding_clean()
        return self.step_apps

    def step_apps(self):
        self.wait_confirm('APPS1')
        self.wait_confirm('APPS2')
        if not self.has_connection():
            self.wait_confirm('APPS_NONET')
        else:
            self.show_highlight_widget('App Center')
            self.wait_confirm('APPS_HASNET')
            self.onboarding_clean()
            askinstall_action = self.show_choices_message('APPS_Q_INSTALL', ('A_YES', None, True),
                     ('A_NO', None, False)).wait() # noqa E501
            if not askinstall_action.future.result():
                self.wait_confirm('APPS_NOINSTALL')
                return self.step_apps_writer
            else:
                return self.step_apps_install

    def step_apps_install(self):
        self.wait_confirm('APPS_INSTALL1')
        self.wait_confirm('APPS_INSTALL2')
        self.wait_confirm('APPS_INSTALL3')
        self.wait_confirm('APPS_INSTALL4')
        self.wait_confirm('APPS_INSTALL5')

    def step_apps_writer(self):
        self.show_highlight_icon('org.libreoffice.LibreOffice.writer')
        self.wait_confirm('OPENWRITER')
        self.onboarding_clean()

        self.show_highlight_fuzzy('center', '75%')
        self.wait_confirm('TYPE')
        self.onboarding_clean()

        # self.show_highlight_rect((self.comp_screenx-500), 0, 500, 250)
        self.wait_confirm('TYPE_MOVEBOX')
        self.onboarding_clean()

        # self.show_highlight_rect((self.comp_screenx-400), 0, 400, 200)
        self.wait_confirm('FILE')
        self.onboarding_clean()

        self.wait_confirm('SAVEDIALOG')

        # self.show_highlight_rect((self.comp_screenx-200), 0, 200, 200)
        self.wait_confirm('CLOSE')
        self.onboarding_clean()

        if self.os_previous == 'win':
            self.wait_confirm('CLOSE_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('CLOSE_MAC')

        self.wait_confirm('APPUSED')
        self.onboarding_clean()
        return self.step_files

    def step_files(self):
        self.wait_confirm('FILES')

        self.show_highlight_widget('Files')
        self.wait_confirm('OPENFILES')
        self.onboarding_clean()

        self.wait_confirm('GOTODOCS')
        self.wait_confirm('THEREITIS')
        return self.step_saveas

    def step_saveas(self):
        self.wait_confirm('SAVEAS1')
        self.wait_confirm('SAVEAS2')
        self.wait_confirm('SAVEAS3')
        self.wait_confirm('SAVEAS4')
        self.wait_confirm('SAVEAS5')
        self.wait_confirm('SAVEAS6')
        return self.step_search

    def step_search(self):
        self.wait_confirm('CLOSEFILES')
        self.show_highlight_widget('search-entry')
        self.wait_confirm('FINDBYNAME')
        self.onboarding_clean()
        self.show_highlight_widget('searchResults')
        self.wait_confirm('RESULTS')
        self.onboarding_clean()
        self.wait_confirm('OPENAGAIN')
        self.wait_confirm('SEARCHMORE')
        if self.has_connection():
            self.wait_confirm('SEARCHWEB1')
            self.wait_confirm('SEARCHWEB2')
        return self.step_switchandmore

    def step_switchandmore(self):
        self.wait_confirm('SWITCHAPPS1')
        self.wait_confirm('SWITCHAPPS2')
        self.wait_confirm('SWITCHAPPS3')
        self.wait_confirm('SWITCHAPPS4')
        # TODO: break this out when/if we decide it's the right thing
        askmore_action = self.show_choices_message('Q_KNOWMORE',
                                                   ('A_HACK', None, 1),
                                                   ('A_HOW', None, 2)
                                                   ('A_PROGRESS', None, 3)).wait()
        if askmore_action.future.result() == 1:
            self.wait_confirm('WHATSHACK')
        if askmore_action.future.result() == 2:
            self.wait_confirm('HOWDOI')
        if askmore_action.future.result() == 3:
            self.wait_confirm('KEEPGOING')
        return self.step_settings

    def step_settings(self):
        self.wait_confirm('SETTINGS1')
        self.wait_confirm('SETTINGS2')

        # self.show_highlight_rect((self.comp_screenx-400), (self.comp_screeny-200), 400, 200)
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

        # self.show_highlight_rect((self.comp_screenx-100), (self.comp_screeny-100), 100, 100)
        self.show_highlight_widget('panelRight')
        self.wait_confirm('SETTINGS8')
        self.onboarding_clean()

        self.wait_confirm('SETTINGS9')
        self.wait_confirm('SETTINGS10')
        self.wait_confirm('SETTINGS11')
        self.wait_confirm('SETTINGS12')
        self.wait_confirm('SETTINGS13')
        self.wait_confirm('SETTINGS14')

        if self.comp_islaptop:
            self.wait_confirm('SETTINGS_LAP_PWR')
        self.wait_confirm('SETTINGS15')
        return self.step_updates

    def step_updates(self):
        self.wait_confirm('UPDATES1')
        self.wait_confirm('UPDATES2')
        self.wait_confirm('UPDATES3')
        self.wait_confirm('UPDATES4')
        self.wait_confirm('UPDATES5')
        return self.step_ending

    def step_ending(self):
        self.wait_confirm('ENDING1')
        self.wait_confirm('ENDING2')
        self.wait_confirm('ENDING3')
        self.wait_confirm('ENDING4')
        super().step_complete_and_stop()

    def step_abort(self):
        self.onboarding_clean()
        super().step_abort()
