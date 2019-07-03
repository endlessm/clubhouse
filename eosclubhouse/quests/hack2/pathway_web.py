from eosclubhouse.libquest import PathWay, Registry


class WebPathWay(PathWay):

    __pathway_name__ = 'Web'


Registry.register_quest_set(WebPathWay)
