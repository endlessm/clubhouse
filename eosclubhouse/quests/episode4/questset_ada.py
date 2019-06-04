from eosclubhouse.libquest import Registry, QuestSet


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = ['MazePt1', 'MazePt2', 'LeviHackdex', 'MazePt3', 'MazePt4']

    def __init__(self):
        super().__init__()


Registry.register_quest_set(AdaQuestSet)
