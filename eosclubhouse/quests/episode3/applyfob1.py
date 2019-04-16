from eosclubhouse.libquest import Quest, Registry
from eosclubhouse.system import Sound


class ApplyFob1(Quest):

    def __init__(self):
        super().__init__('ApplyFob1', 'ada')

    def step_begin(self):
        if not self.clubhouse_state.window_is_visible:
            self.show_hints_message('OPEN_CLUBHOUSE')
        self.connect_clubhouse_changes(['window-is-visible']).wait()

        if not self.wait_confirm('APPLY').is_cancelled():
            trap_questset = Registry.get_quest_set_by_name('TrapQuestSet')
            trap_questset.body_animation = 'panels1'

            self.gss.update('item.fob.1', {'used': True},
                            value_if_missing={'consume_after_use': True})

            self.wait_confirm('OPEN')
            self.wait_confirm('RILEY1')
            self.wait_confirm('RILEY2')
            self.wait_confirm('RILEY3')

        return self.step_success

    def step_success(self):
        self.wait_confirm('END')
        Sound.play('quests/quest-complete')
        self.complete = True
        self.available = False
        self.stop()
