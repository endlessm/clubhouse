from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.cesdemo.fizzics2 import Fizzics2


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __position__ = (279, 260)
    __quests__ = [Fizzics2]

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_RILEY_ADA')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_RILEY_SANIEL')

        return QS('NOQUEST_RILEY_NOTHING')


Registry.register_quest_set(RileyQuestSet)
