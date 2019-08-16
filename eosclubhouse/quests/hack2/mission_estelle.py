from eosclubhouse.libquest import CharacterMission, Registry


class EstelleMission(CharacterMission):

    __character_id__ = 'estelle'


Registry.register_quest_set(EstelleMission)
