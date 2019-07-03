from eosclubhouse.libquest import CharacterMission, Registry


class AdaMission(CharacterMission):

    __character_id__ = 'ada'


Registry.register_quest_set(AdaMission)
