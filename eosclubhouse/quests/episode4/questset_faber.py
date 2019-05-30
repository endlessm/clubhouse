from eosclubhouse.libquest import Registry, QuestSet


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = ['LightspeedKey']

    def __init__(self):
        super().__init__()


Registry.register_quest_set(FaberQuestSet)
