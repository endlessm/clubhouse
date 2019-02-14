
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __position__ = (72, 659)
    __quests__ = []

    def __init__(self):
        super().__init__()

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_SANIEL_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_SANIEL_RILEY')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_SANIEL_FABER')

        return QS('NOQUEST_SANIEL_NOTHING')


Registry.register_quest_set(SanielQuestSet)
