from eosclubhouse.libquest import QuestSet, Registry


class MakerPathWay(QuestSet):

    __pathway_name__ = 'Maker'
    __character_id__ = 'faber'


Registry.register_quest_set(MakerPathWay)
