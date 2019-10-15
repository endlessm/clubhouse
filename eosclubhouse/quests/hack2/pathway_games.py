from eosclubhouse.libquest import QuestSet, Registry


class GamesPathWay(QuestSet):

    __pathway_name__ = 'Games'
    __character_id__ = 'ada'


Registry.register_quest_set(GamesPathWay)
