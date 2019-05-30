from eosclubhouse.libquest import Registry, QuestSet


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = ['FizzicsPuzzle1', 'FizzicsPuzzle2', 'ApplyFob3']


Registry.register_quest_set(FaberQuestSet)
