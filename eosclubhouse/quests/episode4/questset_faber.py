from eosclubhouse.libquest import Registry, QuestSet


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = ['LightspeedKey']


Registry.register_quest_set(FaberQuestSet)
