from eosclubhouse.libquest import Registry, QuestSet


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = []


Registry.register_quest_set(AdaQuestSet)
