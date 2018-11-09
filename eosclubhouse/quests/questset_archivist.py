
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.hackdexcorruption import HackdexCorruption


class ArchivistQuestSet(QuestSet):

    __character_id__ = 'archivist'
    __position__ = (72, 664)
    __quests__ = [HackdexCorruption()]

    def __init__(self):
        super().__init__()
        self.update_visibility()
        first_quest = self.get_quests()[0]
        first_quest.gss.connect('changed', self.update_visibility)

    def update_visibility(self, gss=None):
        first_quest = self.get_quests()[0]
        self.visible = (first_quest.available or first_quest.conf['complete'] or
                        first_quest.is_named_quest_complete('OSIntro'))

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_ARCHIVIST_ADA')
        if Registry.get_quest_set_by_name('RickyQuestSet').is_active():
            return QS('NOQUEST_ARCHIVIST_RICKY')

        quest = self.get_quests()[0]
        if (quest.is_named_quest_complete("LostFiles")):
            return QS('NOQUEST_ARCHIVIST_CHAPTER1END')

        return QS('NOQUEST_ARCHIVIST_NOTHING')


Registry.register_quest_set(ArchivistQuestSet)
