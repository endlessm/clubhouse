from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class ApplyFob2(Quest):

    def __init__(self):
        super().__init__('ApplyFob2', 'saniel')

    def step_begin(self):
        if not self.clubhouse_state.window_is_visible:
            self.show_hints_message('OPEN_CLUBHOUSE')
        self.connect_clubhouse_changes(['window-is-visible']).wait()

        self.wait_confirm('APPLY')

        self.gss.update('clubhouse.character.Trap', {'body-animation': 'panels2'}, {})

        self.gss.update('item.fob.2', {'used': True},
                        value_if_missing={'consume_after_use': True})

        self.wait_confirm('OPEN')
        self.wait_confirm('RILEY')

        return self.step_success

    def step_success(self):
        self.wait_confirm('END')
        Sound.play('quests/quest-complete')
        self.complete = True
        self.available = False
        self.stop()
