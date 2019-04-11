from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService
from eosclubhouse.quests.episode4.mazept1 import MazePt1  # name of the file (with folder) --> import --> name of the class defined in that file.  import basically copy/pastes the code here.
#from eosclubhouse.quests.episode4.mazept2 import MazePt2
#from eosclubhouse.quests.episode4.mazept3 import MazePt3
#from eosclubhouse.quests.episode4.mazept4 import MazePt4
#from eosclubhouse.quests.episode4.bonusround import BonusRound


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __quests__ = [MazePt1]  #, MazePt2, MazePt3, MazePt4, BonusRound]

 #   def __init__(self):
 ##       super().__init__()
 #       gss = GameStateService()
 #       gss.connect('changed', self.update_visibility)
 #       self.update_visibility(gss)

	
 #   def update_visibility(self, gss):
 #       riley_state = gss.get('clubhouse.character.Riley')
 #       self.visible = riley_state is None or not riley_state.get('in_trap', False)


    # what Riley says if she doesn't have any quest to offer
    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_RILEY_ADA')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_RILEY_SANIEL')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_RILEY_FABER')

        return QS('NOQUEST_RILEY_NOTHING')


Registry.register_quest_set(RileyQuestSet)
