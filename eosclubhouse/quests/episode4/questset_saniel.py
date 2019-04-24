from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode4.fizzicskey import FizzicsKey


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = [FizzicsKey]

    def __init__(self):
        super().__init__()


Registry.register_quest_set(SanielQuestSet)
