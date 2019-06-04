from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class LeviHackdex(Quest):

    __items_on_completion__ = {'item.key.levi_hackdex.1': {}}

    APP_NAME = 'com.endlessm.Hackdex_chapter_two'
    ROTATION = 'app.com_endlessm_Hackdex_chapter_two.encryption'
    TOOLBOX_PANEL = 'lock.com.endlessm.Hackdex_chapter_two.1'

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        self.firstflip = True
        return self.step_detect_progress

    @Quest.with_app_launched(APP_NAME)
    def step_detect_progress(self):
        # app is running, have they already unlocked it?
        if self.is_panel_unlocked(self.TOOLBOX_PANEL):
            return self.step_wait_until_solved
        else:
            # no key, first play
            return self.step_introduction

    @Quest.with_app_launched(APP_NAME)
    def step_introduction(self):
        for message_id in ['OPENINTRO', 'OPENINTRO1', 'OPENINTRO2',
                           'OPENINTRO3', 'OPENINTRO4', 'PREFLIP',
                           'GIVEKEY']:
            self.wait_confirm(message_id)
        self.give_item('item.key.levi_hackdex.1')
        return self.step_wait_for_unlock

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_unlock(self):
        if self.is_panel_unlocked(self.TOOLBOX_PANEL):
            self.pause(1)
            self.wait_confirm('UNLOCK')
            self.pause(1)
            return self.step_wait_until_solved
        else:
            return self.step_wait_for_unlock

    def step_wait_until_solved(self):
        if not self._app.is_running():
            return self.abort
        data = self.gss.get('app.com_endlessm_Hackdex_chapter_two.encryption')
        if data is None:
            self.show_hints_message("DECRYPT")
        elif data.get('rotation') == 5:
            return self.step_part2
        else:
            if self.firstflip:
                self.wait_confirm("DECRYPT2")
                self.firstflip = False
            self.show_hints_message("DECRYPT3")
        # (From Hackdex 1)
        # The HackDex app is restarted when its parameters are changed and the app is flipped
        # back, so we check that and give it time before considering it has stopped running.
        self.connect_app_quit(self._app).wait()
        self.wait_for_app_launch(self._app, timeout=10)
        return self.step_wait_until_solved

    def step_part2(self):
        self.pause(3)
        for message_id in ['DECRYPT_SUCCESS', 'BACKGROUND', 'PUSHINSTRUCTION',
                           'PUSHINSTRUCTION2', 'PUSHINSTRUCTION3', 'PUSHINSTRUCTION4',
                           'PUSHINSTRUCTION5', 'PUSHINSTRUCTION6']:
            self.wait_confirm(message_id)
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
