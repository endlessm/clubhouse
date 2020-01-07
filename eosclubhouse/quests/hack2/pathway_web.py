from eosclubhouse.libquest import QuestSet, Registry


class WebPathWay(QuestSet):

    __pathway_order__ = 2
    __pathway_name__ = 'Web'
    __character_id__ = 'riley'


Registry.register_quest_set(WebPathWay)
