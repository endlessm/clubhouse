from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class LeviHackdex(Quest):

    APP_NAME = 'com.endlessm.Hackdex_chapter_two'
    ROTATION = 'app.com_endlessm_Hackdex_chapter_two.encryption'

    def __init__(self):
        super().__init__('LeviHackdex', 'ada')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_detect_progress

    def step_detect_progress(self):
        # is the app running? launch it
        if not self._app.is_running():
            return self.step_begin
        # app is running, do they already have the key?
        key = self.gss.get('item.key.levi_hackdex.1')
        if key is not None:
            return self.step_wait_for_unlock
        else:
            # no key, first play
            return self.step_part1

    @Quest.with_app_launched(APP_NAME)
    def step_part1(self):
        self.wait_confirm('OPENINTRO')
        self.wait_confirm('OPENINTRO1')
        self.wait_confirm('OPENINTRO2')
        self.wait_confirm('OPENINTRO3')
        self.wait_confirm('GIVEKEY')
        self.give_item('item.key.levi_hackdex.1')
        return self.step_detect_progress

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_unlock(self):
        self.wait_confirm('FLIP')
        lock_state = self.gss.get('lock.com.endlessm.Hackdex_chapter_two.1')
        if lock_state is not None and not lock_state.get('locked'):
            self.wait_confirm('DECRYPT')
            return self.step_wait_until_solved
        else:
            self.wait_confirm('UNLOCK')
            return self.step_wait_for_unlock

    def step_wait_until_solved(self):
        if not self._app.is_running():
            return self.abort
        # is the rotation correct?
        data = self.gss.get('app.com_endlessm_Hackdex_chapter_two.encryption')
        if data is None:
            return self.abort

        if data.get('rotation') == 5:
            return self.step_part2
        # (From Hackdex 1)
        # The HackDex app is restarted when its parameters are changed and the app is flipped
        # back, so we check that and give it time before considering it has stopped running.
        self.connect_app_quit(self._app).wait()
        self.wait_for_app_launch(self._app, timeout=2)
        return self.step_wait_until_solved

    @Quest.with_app_launched(APP_NAME)
    def step_part2(self):
        self.wait_confirm('DECRYPT_SUCCESS')
        self.wait_confirm('BACKGROUND')
        self.wait_confirm('PUSHINSTRUCTION')
        self.wait_confirm('PUSHINSTRUCTION2')
        self.wait_confirm('PUSHINSTRUCTION3')
        self.wait_confirm('PUSHINSTRUCTION4')
        self.wait_confirm('PUSHINSTRUCTION5')
        self.wait_confirm('PUSHINSTRUCTION6')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
