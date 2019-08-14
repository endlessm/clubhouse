from eosclubhouse.libquest import CharacterMission, Registry


class RileyMission(CharacterMission):

    __character_id__ = 'riley'


Registry.register_quest_set(RileyMission)
