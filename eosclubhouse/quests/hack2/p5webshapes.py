from eosclubhouse.libquest import Quest
import os


class P5WebShapes(Quest):

    __tags__ = ['pathway:web', 'skillset:LaunchQuests']
    __pathway_order__ = 400

    def step_begin(self):
        self.wait_confirm('WELCOME')
        os.system('xdg-open https://editor.p5js.org/p5/sketches/Hello_P5:_shapes')
        return self.step_complete_and_stop
