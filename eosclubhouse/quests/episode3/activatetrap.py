from eosclubhouse.libquest import Quest, Registry
from eosclubhouse.system import Sound


class ActivateTrap(Quest):

    __available_after_completing_quests__ = ['ApplyFob3']
    __complete_episode__ = True

    def __init__(self):
        super().__init__('ActivateTrap', 'saniel')

    def step_begin(self):
        if not self.clubhouse_state.window_is_visible:
            self.show_hints_message('OPEN_CLUBHOUSE')
        self.connect_clubhouse_changes(['window-is-visible']).wait()

        self.wait_confirm('TRY')
        for message in range(2, 6):
            self.wait_confirm('TRY{}'.format(message))

        trap_questset = Registry.get_quest_set_by_name('TrapQuestSet')

        trap_questset.body_animation = 'transcoding-init'

        self.wait_confirm('TRANSCODING')

        trap_questset.body_animation = 'transcoding'

        return self.step_success

    def step_success(self):
        self.show_confirm_message('END', confirm_label='End of Episode 3').wait()
        if not self.confirmed_step():
            return

        Sound.play('quests/quest-complete')
        self.complete = True
        self.available = False
        self.stop()
