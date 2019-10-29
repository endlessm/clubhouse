from eosclubhouse.libquest import Quest


class Migration(Quest):

    __tags__ = ['pathway:games']

    def setup(self):
        self.skippable = True

    def step_begin(self):
        self.wait_confirm('WELCOME')
        return self.step_complete_and_stop
