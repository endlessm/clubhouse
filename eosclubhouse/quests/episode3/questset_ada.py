
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode3.setup import SetUp
from eosclubhouse.quests.episode3.rileyslevels import RileysLevels


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 206)
    __quests__ = [SetUp, RileysLevels]

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_ADA_SANIEL')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_ADA_FABER')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
