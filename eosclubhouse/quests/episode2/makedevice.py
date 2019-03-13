from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from gi.repository import GObject
from eosclubhouse.utils import QS


class MakeDevice(Quest):

    def __init__(self):
        super().__init__('MakeDevice', 'faber')

    def has_all_stealth_items(self):
        items = ['item.stealth.1', 'item.stealth.2', 'item.stealth.3', 'item.stealth.4']
        for item in items:
            if self.gss.get(item) is None:
                return False
        return True

    @GObject.Property(type=str)
    def accept_label(self):
        if self.has_all_stealth_items():
            return QS('{}_QUEST_ACCEPT'.format(self._qs_base_id))
        else:
            return QS('{}_QUEST_NOTYET'.format(self._qs_base_id))

    def step_begin(self):
        if not self.has_all_stealth_items():
            return self.step_missing_items

        self.wait_confirm('EXPLAIN')

        if not self.wait_confirm('GIVEITEM').is_cancelled():
            self.give_item('item.stealth_device')

        self.wait_confirm('RILEY')

        return self.step_end

    def step_missing_items(self):
        # @todo: We should show some message here if some items are missing, otherwise
        # the quest ends abruptely.
        self.stop()

    def step_end(self):
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
