
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse import logger
from eosclubhouse.quests.episode4.mazept2 import MazePt2
from eosclubhouse.quests.episode4.levihackdex import LeviHackdex
from eosclubhouse.quests.episode4.mazept3 import MazePt3
from eosclubhouse.quests.episode4.mazept4 import MazePt4

class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 186)
    __quests__ = [MazePt2, LeviHackdex, MazePt3, MazePt4]

    def __init__(self):
        super().__init__()
        
    def get_empty_message(self):
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_ADA_SANIEL')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_ADA_FABER')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_ADA_RILEY')
        return QS('NOQUEST_ADA_NOTHING')

Registry.register_quest_set(AdaQuestSet)
