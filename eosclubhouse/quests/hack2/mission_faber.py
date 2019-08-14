from eosclubhouse.libquest import CharacterMission, Registry


class FaberMission(CharacterMission):

    __character_id__ = 'faber'


Registry.register_quest_set(FaberMission)
