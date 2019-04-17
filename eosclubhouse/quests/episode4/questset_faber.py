
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse import logger
from eosclubhouse.quests.episode4.lightspeed import Lightspeed

class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = [Lightspeed]

    def __init__(self):
        super().__init__()
        
    def get_empty_message(self):
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_FABER_SANIEL')
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_FABER_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_FABER_RILEY')
        return QS('NOQUEST_FABER_NOTHING')

Registry.register_quest_set(FaberQuestSet)
