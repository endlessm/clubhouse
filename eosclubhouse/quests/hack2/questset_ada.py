from eosclubhouse.libquest import QuestSet, Registry


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = ['FirstContact']


Registry.register_quest_set(AdaQuestSet)
