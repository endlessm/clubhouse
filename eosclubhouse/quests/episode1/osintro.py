from eosclubhouse.libquest import Registry, Quest
from eosclubhouse.system import Desktop, App, Sound


class OSIntro(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('OS Intro', 'ada')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.wait_confirm('PRELAUNCH')
        return self.step_launch

    def step_launch(self):
        self.show_hints_message('LAUNCH')

        if not self._app.is_running():
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(self.APP_NAME)
            Desktop.focus_app(self.APP_NAME)
            self.wait_for_app_launch(self._app)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        if self._app.get_js_property('flipped'):
            return self.step_saniel_flip

        msg_id = 'CLICK' if self._app.get_js_property('clicked') else 'EXPLANATION'
        confirm_action = self.show_confirm_message(msg_id)
        app_changes_action = self.connect_app_js_props_changes(self._app, ['flipped', 'clicked'])

        self.wait_for_one([confirm_action, app_changes_action])

        if self.confirmed_step():
            return self.step_saniel

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_saniel(self):
        if self._app.get_js_property('flipped'):
            return self.step_flipped, self.step_saniel

        Sound.play('quests/saniel-intro')
        confirm_action = self.show_confirm_message('SANIEL')
        app_changes_action = self.connect_app_js_props_changes(self._app, ['flipped'])

        self.wait_for_one([confirm_action, app_changes_action])
        if self.confirmed_step():
            return self.step_intro

        return self.step_saniel

    @Quest.with_app_launched(APP_NAME)
    def step_saniel_flip(self):
        if not self._app.get_js_property('flipped'):
            return self.step_intro

        Sound.play('quests/saniel-angry')
        self.show_hints_message('SANIEL_FLIP')
        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_saniel_flip

    @Quest.with_app_launched(APP_NAME)
    def step_intro(self):
        confirm_action = self.show_confirm_message('INTRO')
        app_changes_action = self.connect_app_js_props_changes(self._app, ['flipped'])

        self.wait_for_one([confirm_action, app_changes_action])

        if self.confirmed_step():
            return self.step_saniel2

        if self._app.get_js_property('flipped'):
            return self.step_flipped, self.step_intro

        return self.step_intro

    @Quest.with_app_launched(APP_NAME)
    def step_saniel2(self):
        confirm_action = self.show_confirm_message('SANIEL2')
        app_changes_action = self.connect_app_js_props_changes(self._app, ['flipped'])

        self.wait_for_one([confirm_action, app_changes_action])

        if self.confirmed_step():
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            return self.step_wrapup

        if self._app.get_js_property('flipped'):
            return self.step_flipped, self.step_saniel2

        return self.step_saniel2

    @Quest.with_app_launched(APP_NAME)
    def step_wrapup(self):
        confirm_action = self.show_confirm_message('WRAPUP')
        app_changes_action = self.connect_app_js_props_changes(self._app, ['flipped'])

        self.wait_for_one([confirm_action, app_changes_action])

        if self.confirmed_step():
            # this is the quest that makes Saniel appear
            saniel_questset = Registry.get_quest_set_by_name('SanielQuestSet')
            if saniel_questset is not None:
                saniel_questset.visible = True
            return self.stop

        if self._app.get_js_property('flipped'):
            return self.step_flipped, self.step_wrapup

        return self.step_saniel2

    @Quest.with_app_launched(APP_NAME)
    def step_flipped(self, next_step):
        Sound.play('quests/saniel-angry')
        self.show_hints_message('FLIPPED')
        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return next_step
