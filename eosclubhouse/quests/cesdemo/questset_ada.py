
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 206)
    __quests__ = []

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_ADA_RILEY')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_ADA_SANIEL')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
