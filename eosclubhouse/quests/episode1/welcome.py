from eosclubhouse.libquest import Quest


class Welcome(Quest):

    # The quest doesn't show any messages immediately to the user, so let's silence it when it runs.
    __sound_on_run_begin__ = None

    def __init__(self):
        # This quest starts directly. There's no prompting.
        super().__init__('Welcome', 'ada', '')

        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = False
        self.skippable = True

        # This quest should only be run in the first login, however, for existing users who have
        # upgraded, we check if the FizzicsIntro (first quest) is done as a way to verify whether
        # they have used the Clubhouse before.
        if not self.complete and self.is_named_quest_complete("FizzicsIntro"):
            self.complete = True
            self.save_conf()

    def _check_visible(self):
        return self.clubhouse_state.window_is_visible

    def step_begin(self):
        if self.complete or self._check_visible():
            return self.step_abort

        self.connect_clubhouse_changes(['window-is-visible']).wait(timeout=5)
        if self._check_visible():
            # Window opened in less than 5 seconds; we silently quit because the user is in the
            # right path.
            return self.step_abort

        self.show_hints_message('WELCOME')
        self.connect_clubhouse_changes(['window-is-visible']).wait()

        msg_id = 'SUCCESS' if self._check_visible() else None
        return self.step_abort, msg_id

    def step_abort(self, msg_id=None):
        self.complete = True
        if msg_id is not None:
            # Save conf before pausing since we don't want to eventually allow the user to cancel
            # this quest, which would make it show up automatically again the next time the
            # Clubhouse is run.
            self.save_conf()

            self.pause(.5)
            self.show_message(msg_id)
            self.pause(5)
        self.stop()

    def set_to_background(self):
        # We don't want this quest running in the background, if the quest message is closed, we
        # immediately abort the quest.
        self.step_abort()
