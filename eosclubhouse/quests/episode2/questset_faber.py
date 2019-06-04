from eosclubhouse.libquest import Registry, QuestSet


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = ['MakerIntro', 'StealthDevice', 'MakerQuest', 'MakeDevice']

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = (first_quest.available or first_quest.conf['complete'] or
                        first_quest.is_named_quest_complete('Investigation'))


Registry.register_quest_set(FaberQuestSet)
