from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.fizzics1 import Fizzics1
from eosclubhouse.quests.breaksomething import BreakSomething
from eosclubhouse.quests.fizzics2 import Fizzics2


class RickyQuestSet(QuestSet):

    __character_id__ = 'ricky'
    __position__ = (279, 282)
    __quests__ = [Fizzics1(), BreakSomething(), Fizzics2()]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = first_quest.available or first_quest.conf['complete']

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_RICKY_ADA')
        if Registry.get_quest_set_by_name('ArchivistQuestSet').is_active():
            return QS('NOQUEST_RICKY_ARCHIVIST')

        return QS('NOQUEST_RICKY_NOTHING')


Registry.register_quest_set(RickyQuestSet)
