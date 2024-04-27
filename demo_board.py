from typing import List, Callable, Set

import demo_cards as dc
from enums import Icon


class Location:
    def __init__(self, name: str, requirement: dc.Requirement, effect: dc.Effect,
                 icons: Set[Icon] = {Icon.IMPERIUM, Icon.DESERT, Icon.FREMEN}):
        self.name: str = name
        self.requirement: dc.Requirement = requirement
        self.effect: dc.Effect = effect
        self.is_occupied: bool = False
        self.icons: Set[Icon] = icons

    def occupy(self, game: 'Game'):
        self.is_occupied = True
        self.requirement.fulfill(game)
        self.effect.execute(game)

    def __repr__(self):
        return self.name + str(self.icons)




spice_requirement = dc.Requirement(lambda game: game.current_player.spice >= 2, lambda game: game.current_player.change_spice(-2))
garrison_effect = dc.Effect(lambda game: game.current_player.change_garrison(2))

locations = [
    Location("Spice Mine", dc.NoRequirement(), dc.spice_effect, icons={Icon.IMPERIUM, Icon.DESERT}),
    Location("Fremen Outpost", spice_requirement, garrison_effect, icons={Icon.FREMEN}),
]
