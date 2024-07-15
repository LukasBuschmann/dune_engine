from typing import Callable, Any

from enums import Faction


class Requirement:
    def __init__(self, requirement: Callable[['Player'], bool], fulfillment: Callable[['Player'], Any]):
        self.requirement: Callable[['Player'], bool] = requirement
        self.fulfillment: Callable[['Player'], Any] = fulfillment

    def is_met(self, player: 'Player'):
        return self.requirement(player)

    def fulfill(self, player: 'Player'):
        self.fulfillment(player)

    def __add__(self, other: 'Requirement'):
        return Requirement(
            requirement=lambda player: self.is_met(player) and other.is_met(player),
            fulfillment=lambda player: (self.fulfill(player), other.fulfill(player))
        )


def spice_requirement(spice: int) -> Requirement:
    return Requirement(lambda player: player.spice >= spice, lambda player: player.change_spice(-spice))


def solari_requirement(solari: int) -> Requirement:
    return Requirement(lambda player: player.solari >= solari, lambda player: player.change_solari(-solari))


def water_requirement(water: int) -> Requirement:
    return Requirement(lambda player: player.water >= water, lambda player: player.change_water(-water))


def influence_requirement(faction: 'Faction', influence: int) -> Requirement:
    return Requirement(lambda player: player.factions[faction]['influence'] >= influence, lambda player: None)


def alliance_requirement(faction: 'Faction') -> Requirement:
    return Requirement(lambda player: faction in player.alliances, lambda player: None)


# including the card itself
def in_play_requirement(faction: 'Faction', n: int) -> Requirement:
    return Requirement(lambda player: player.get_in_play(faction) > n, lambda player: None)


def trash_card_requirement(name: str) -> Requirement:
    # a bit hacky, but works. Only use this for agent effects
    return Requirement(
        requirement=lambda player: True,
        fulfillment=lambda player: player.played_cards.remove(
            list(filter(lambda card: card.name == name, player.played_cards))))


fremen_bond_requirement = Requirement(lambda player: player.get_in_play_and_hand(Faction.FREMEN) > 1,
                                      lambda player: None)

no_sword_master_requirement = Requirement(lambda player: player.max_agents < 3, lambda player: None)

not_in_high_council_requirement = Requirement(lambda player: not player.is_in_high_council(), lambda player: None)

no_requirement = Requirement(lambda player: True, lambda player: None)
