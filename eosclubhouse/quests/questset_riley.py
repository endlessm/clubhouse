from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.fizzics1 import Fizzics1
from eosclubhouse.quests.breaksomething import BreakSomething
from eosclubhouse.quests.fizzics2 import Fizzics2
from eosclubhouse.quests.fizzicscode2 import FizzicsCode2


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __position__ = (279, 260)
    __quests__ = [Fizzics1, BreakSomething, Fizzics2, FizzicsCode2]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = first_quest.available or first_quest.conf['complete']

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_RILEY_ADA')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_RILEY_SANIEL')

        quest = self.get_quests()[0]
        if (quest.is_named_quest_complete("FizzicsCode2")):
            return QS('NOQUEST_RILEY_CHAPTER1END')

        return QS('NOQUEST_RILEY_NOTHING')


Registry.register_quest_set(RileyQuestSet)
