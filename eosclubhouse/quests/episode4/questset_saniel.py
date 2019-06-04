from eosclubhouse.libquest import Registry, QuestSet


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = ['FizzicsKey']


Registry.register_quest_set(SanielQuestSet)
