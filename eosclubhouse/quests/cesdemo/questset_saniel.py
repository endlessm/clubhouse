
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = []

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_SANIEL_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_SANIEL_RILEY')

        return QS('NOQUEST_SANIEL_NOTHING')


Registry.register_quest_set(SanielQuestSet)
