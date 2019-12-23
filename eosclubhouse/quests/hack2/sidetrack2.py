from eosclubhouse.libquest import Quest


class Sidetrack2(Quest):

    __app_id__ = 'com.hack_computer.Sidetrack'

    __available_after_completing_quests__ = ['Sidetrack1']
    __tags__ = ['pathway:games', 'difficulty:medium', 'skillset:LaunchQuests']
    __pathway_order__ = 100

    def step_begin(self):
        self.wait_confirm('NOQUEST_TRAP_NOTHING', confirm_label='Got it!')
        return self.step_complete_and_stop
