from eosclubhouse.libquest import QuestSet, Registry


class GamesPathWay(QuestSet):

    __pathway_order__ = 0
    __pathway_name__ = 'Games'
    __character_id__ = 'ada'


Registry.register_quest_set(GamesPathWay)
