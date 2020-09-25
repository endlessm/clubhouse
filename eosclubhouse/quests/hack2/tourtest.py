from eosclubhouse.libquest import Quest
from eosclubhouse.system import Hostname

# from eosclubhouse import logger


class TourTest(Quest):

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
        return self.step_quiz

    def step_test(self):
        self.wait_for_highlight_rect((self.comp_screenx-500), 0, 500, 250)
        return self.step_abort

    def step_quiz(self):
        self.wait_confirm('QUIZ_INTRO')
        self.comp_isfirst = self.show_choices_message('QUIZ_FIRSTCOMP', ('NOQUEST_POSITIVE', None, True), # noqa E501
                ('NOQUEST_NEGATIVE', None, False)).wait().future.result() # noqa E501

        if self.comp_isfirst:
            self.wait_confirm('QUIZ_ISFIRST')
            return self.step_teachkbm
        else:
            self.wait_confirm('QUIZ_NOTFIRST')

        self.onboarding_image('temp_mac_win.png', size='60% 16:9')
        action = self.show_choices_message('QUIZ_OS', ('QUIZ_OS_WIN', None, True),
                                           ('QUIZ_OS_MAC', None, False)).wait()
        self.onboarding_clean()
        if action.future.result():
            self.os_previous = "win"
        else:
            self.os_previous = "mac"

        self.wait_confirm('QUIZ_END')
        return self.step_greet

    def step_teachkbm(self):
        # TODO: Need images for this section to reduce text
        self.wait_confirm('KBM1')
        self.wait_confirm('MOUSE1')
        self.wait_confirm('MOUSE2')

        if self.comp_islaptop:
            for msgid in ['MOUSE_LAP1', 'MOUSE_LAP2', 'MOUSE_LAP3']:
                self.wait_confirm(msgid)
        else:
            for msgid in ['MOUSE_DESK1', 'MOUSE_DESK2', 'MOUSE_DESK3']:
                self.wait_confirm(msgid)

        self.wait_confirm('KB1')
        self.wait_confirm('KB2')
        self.wait_confirm('KB3')

        if self.comp_islaptop:
            self.wait_confirm('KB_LAP')
        else:
            self.wait_confirm('KB_DESK')

        self.wait_confirm('USE')
        self.wait_confirm('USE1')
        return self.step_use

    def step_greet(self):
        self.wait_confirm('GREET')
        return self.step_use

    def step_use(self):
        self.show_highlight_fuzzy('center', '75%')
        self.wait_confirm('HOME1')
        self.onboarding_clean()

        if self.os_previous == 'win':
            self.wait_confirm('HOME_WIN')
        if self.os_previous == 'mac':
            self.wait_confirm('HOME_MAC')

        self.show_highlight_widget('icon-grid')
        self.wait_confirm('HOME2')
        self.onboarding_clean()

        self.show_highlight_widget('Files')
        self.wait_confirm('DOCS')
        self.onboarding_clean()

        if self.os_previous == 'win':
            self.show_highlight_widget('Files')
            self.wait_confirm('TRASH_WIN')
            self.onboarding_clean()
            self.show_highlight_widget('stEntry')
            self.wait_confirm('STARTMENU1')
            self.onboarding_clean()
            self.show_highlight_widget('App Center')
            self.wait_confirm('STARTMENU2')
            self.onboarding_clean()
        if self.os_previous == 'mac':
            self.show_highlight_widget('Files')
            self.wait_confirm('TRASH_MAC')
            self.onboarding_clean()
            self.show_highlight_widget('stBin')
            self.wait_confirm('SPOTLIGHT1')
            self.onboarding_clean()
            self.show_highlight_widget('App Center')
            self.wait_confirm('SPOTLIGHT2')
            self.onboarding_clean()
        return self.step_apps

    def step_apps(self):
        self.wait_confirm('APPS1')
        self.wait_confirm('APPS2')

        # TODO: highlight app center
        if self.has_connection():
            self.show_highlight_widget('App Center')
            self.wait_confirm('APPS_NET')
            self.onboarding_clean()
        else:
            self.wait_confirm('APPS_NONET')
        self.show_highlight_icon('org.libreoffice.LibreOffice.writer')
        self.wait_confirm('OPENWRITER')
        self.onboarding_clean()

        self.show_highlight_fuzzy('center', '75%')
        self.wait_confirm('TYPE')
        self.onboarding_clean()

        self.show_highlight_rect((self.comp_screenx-500), 0, 500, 250)
        self.wait_confirm('TYPE_MOVEBOX')
        self.onboarding_clean()

        self.show_highlight_rect((self.comp_screenx-400), 0, 400, 200)
        self.wait_confirm('FILE')
        self.onboarding_clean()

        self.wait_confirm('SAVEDIALOG')

        self.show_highlight_rect((self.comp_screenx-200), 0, 200, 200)
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
        self.wait_confirm('FINDBYNAME1')
        self.wait_confirm('FINDBYNAME2')

        self.show_highlight_widget('search-entry')
        # backup in case this ^^ breaks again
        # self.show_highlight_rect(int(self.comp_screenx/2-190), 50, 380, 50)
        self.wait_confirm('USESEARCH')
        self.onboarding_clean()

        self.show_highlight_widget('searchResults')
        self.wait_confirm('RESULTS')
        self.onboarding_clean()

        self.wait_confirm('OPENAGAIN')
        self.wait_confirm('SEARCHLOTS')
        return self.step_settings

    def step_settings(self):
        self.wait_confirm('SETTINGS1')
        self.wait_confirm('SETTINGS2')

        self.show_highlight_rect((self.comp_screenx-400), (self.comp_screeny-200), 400, 200)
        self.wait_confirm('SETTINGS_TRAYICONS')
        self.onboarding_clean()

        self.wait_confirm('SETTINGS_MOVEWIN')
        if self.has_connection():
            self.wait_confirm('SETTINGS_HASNET')
        else:
            self.wait_confirm('SETTINGS_NONET')

        self.wait_confirm('SETTINGS_TRAY_VOL')

        if self.comp_islaptop:
            self.wait_confirm('SETTINGS_LAP_BATT')
        self.wait_confirm('SETTINGS_TRAY_INFO')

        self.show_highlight_rect((self.comp_screenx-100), (self.comp_screeny-100), 100, 100)
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

        return self.step_ending

    def step_ending(self):
        for num in range(1, 10):
            self.wait_confirm('ENDING' + str(num))
        super().step_complete_and_stop()

    def step_abort(self):
        self.onboarding_clean()
        super().step_abort()
