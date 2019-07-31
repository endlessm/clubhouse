from eosclubhouse.libquest import PathWay, Registry


class MakerPathWay(PathWay):

    __pathway_name__ = 'Maker'


Registry.register_quest_set(MakerPathWay)
