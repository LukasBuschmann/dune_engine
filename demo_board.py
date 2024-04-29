from typing import List, Callable, Set

import Requirement
from Effect import Effect
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
        self.effect.execute(game) #ToDo: this wont work for complex effects

    def __repr__(self):
        return self.name + str(self.icons)




spice_requirement = Requirement.SpiceRequirement(2)
garrison_effect = Effect(lambda game: game.current_player.change_garrison(2)) #ToDo: BUG! This gets triggered twice (requirement only once)

locations = [
    Location("Spice Mine", Requirement.noRequirement, dc.spice_effect, icons={Icon.IMPERIUM, Icon.DESERT}),
    Location("Fremen Outpost", spice_requirement, garrison_effect, icons={Icon.FREMEN}),
]
