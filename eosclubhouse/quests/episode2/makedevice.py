from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class MakeDevice(Quest):

    def __init__(self):
        super().__init__('MakeDevice', 'faber')

    def have_all_stealth_items(self):
        return (self.gss.get('item.stealth.1') is not None and
                self.gss.get('item.stealth.2') is not None and
                self.gss.get('item.stealth.3') is not None and
                self.gss.get('item.stealth.4') is not None)

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if not self.have_all_stealth_items():
                self.stop()
                return
            self.show_question('EXPLAIN')

        if self.confirmed_step():
            return self.step_give_item

    def step_give_item(self, time_in_step):
        if time_in_step == 0:
            self.show_question('GIVEITEM')
            self.give_item('item.stealth_device')
        if self.confirmed_step():
            return self.step_riley

    def step_riley(self, time_in_step):
        if time_in_step == 0:
            self.show_question('RILEY')
        if self.confirmed_step():
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('END', confirm_label='Bye')
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
