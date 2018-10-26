from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.fizzics1 import Fizzics1
from eosclubhouse.quests.breaksomething import BreakSomething
from eosclubhouse.quests.fizzics2 import Fizzics2


class RickyQuestSet(QuestSet):

    __character_id__ = 'ricky'
    __position__ = (250, 270)
    __quests__ = [Fizzics1(), BreakSomething(), Fizzics2()]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = first_quest.available or first_quest.conf['complete']

    def get_empty_message(self):
        quest = self.get_quests()[0]
        if quest.is_named_quest_complete("Fizzics1") and \
           not quest.is_named_quest_complete("OSIntro"):
            return QS('NOQUEST_RICKY_ADA')

        if quest.is_named_quest_complete("Fizzics2") and \
           not quest.is_named_quest_complete("HackdexCorruption"):
            return QS('NOQUEST_RICKY_ARCHIVIST')

        return QS('NOQUEST_RICKY_NOTHING')


Registry.register_quest_set(RickyQuestSet)
