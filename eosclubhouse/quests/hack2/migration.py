from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop


class Migration(Quest):

    __tags__ = ['pathway:games']

    def setup(self):
        self.skippable = True

    def step_begin(self):
        Desktop.set_hack_icon_pulse(True)
        self.wait_confirm('WELCOME')
        return self.step_complete_and_stop
