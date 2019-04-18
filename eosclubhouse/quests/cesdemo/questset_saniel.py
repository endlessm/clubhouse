from eosclubhouse.libquest import Registry, QuestSet


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = []


Registry.register_quest_set(SanielQuestSet)
