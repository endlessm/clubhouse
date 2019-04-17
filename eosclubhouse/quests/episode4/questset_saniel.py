
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse import logger
from eosclubhouse.quests.episode4.fizzicskey import FizzicsKey

class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    #__position__ = (ey38, 186)
    __quests__ = [FizzicsKey]

    def __init__(self):
        super().__init__()

    def get_empty_message(self):
        #logger.debug('current quest sets %s', Registry.get_quest_sets())
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_SANIEL_FABER')
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_SANIEL_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_SANIEL_RILEY')
        return QS('NOQUEST_SANIEL_NOTHING')

Registry.register_quest_set(SanielQuestSet)
