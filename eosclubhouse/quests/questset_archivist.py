
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.hackdexcorruption import HackdexCorruption


class ArchivistQuestSet(QuestSet):

    __character_id__ = 'archivist'
    __position__ = (50, 650)
    __quests__ = [HackdexCorruption()]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = first_quest.available or first_quest.conf['complete']

    def get_empty_message(self):
        quest = self.get_quests()[0]
        if quest.is_named_quest_complete("HackdexCorruption") and \
           not quest.is_named_quest_complete("Fizzics2"):
            return QS('NOQUEST_ARCHIVIST_RICKY')

        return QS('NOQUEST_ARCHIVIST_NOTHING')


Registry.register_quest_set(ArchivistQuestSet)
