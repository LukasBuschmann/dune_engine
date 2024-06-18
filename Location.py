from typing import List, Callable, Set, Any

from Requirement import SpiceRequirement, noRequirement, NoFullfillmentRequirement, Requirement, SolariRequirement, \
    WaterRequirement, InfluenceRequirement, Choice
from Effect import Effect, SpiceEffect, GarrisonEffect, spice_trade, SolariEffect, PersuasionEffect, GarrisonEffect, \
    DeployEffect, ChoicelessEffect, CardEffect, MentatEffect, WormSpiceEffect, CaptureSpiceEffect, CaptureSolariEffect, \
    IntrigueEffect, InfluenceEffect, WaterEffect, FoldSpaceEffect, RemoveCardEffect, StealIntrigueEffect
import Cards as dc
from enums import Icon, Faction, ChoiceType


class Location:
    def __init__(self,
                 name: str,
                 requirement: dc.Requirement,
                 effect: dc.Effect,
                 icons: Set[Icon],
                 faction: Faction = None):
        self.name: str = name
        self.requirement: dc.Requirement = requirement
        self.effect: dc.Effect = effect
        self.is_occupied: bool = False
        self.icons: Set[Icon] = icons
        self.faction: Faction = faction

    def occupy(self):
        self.is_occupied = True

    def clear(self):
        self.is_occupied = False

    def is_available_with(self, game: 'Game', card: dc.Card):
        if self.icons.intersection(card.icons):
            if not self.is_occupied:
                if self.requirement.is_met(game):
                    return True
        return False
    def __repr__(self):
        return self.name.lower() if self.is_occupied else self.name.upper()

    def __str__(self):
        return self.name + (str(self.icons) if len(self.icons) > 0 else "")


faction_rewards = {
    Faction.EMPEROR: GarrisonEffect(2),
    Faction.SPACING_GUILD: SolariEffect(3),
    Faction.BENE_GESSERIT: IntrigueEffect(),
    Faction.FREMEN: WaterEffect(1),
}

locations = [
    Location(
        name="Imperial Basin",
        requirement=noRequirement,
        effect=SpiceEffect(1) + DeployEffect(2) + WormSpiceEffect() + CaptureSpiceEffect(1),
        icons={Icon.ECONOMY},
    ),
    Location(
        name="Hagga Basin",
        requirement=WaterRequirement(1),
        effect=SpiceEffect(2) + DeployEffect(2) + WormSpiceEffect(),
        icons={Icon.ECONOMY},
    ),
    Location(
        name="The Great Flat",
        requirement=WaterRequirement(2),
        effect=SpiceEffect(3) + DeployEffect(2) + WormSpiceEffect(),
        icons={Icon.ECONOMY},
    ),
    Location(
        name="Sell Melange",
        requirement=SpiceRequirement(2),
        effect=spice_trade,
        icons={Icon.ECONOMY}
    ),
    Location(
        name="Secure Contract",
        requirement=noRequirement,
        effect=SolariEffect(3),
        icons={Icon.ECONOMY}
    ),

    Location(
        name="Hall Of Oratory",
        requirement=noRequirement,
        effect=GarrisonEffect(1) + PersuasionEffect(1),
        icons={Icon.STATECRAFT}
    ),
    Location(
        name="Swordmaster",
        requirement=SolariRequirement(8) + NoFullfillmentRequirement(lambda game: game.current_player.max_agents < 3),
        effect=ChoicelessEffect(lambda game: game.current_player.add_mentat()),
        icons={Icon.STATECRAFT}
    ),
    Location(
        name="Rally Troops",
        requirement=SolariRequirement(4),
        effect=GarrisonEffect(4),
        icons={Icon.STATECRAFT}
    ),
    Location(
        name="Mentat",
        requirement=SolariRequirement(2) + NoFullfillmentRequirement(lambda game: game.mentat_is_available()),
        effect=CardEffect(1) + MentatEffect(),
        icons={Icon.STATECRAFT}
    ),
    Location(
        name="High Council",
        requirement=SolariRequirement(5) + NoFullfillmentRequirement(
            lambda game: not game.current_player.is_in_high_council()),
        effect=ChoicelessEffect(lambda game: game.current_player.enter_high_council()),
        icons={Icon.STATECRAFT}
    ),

    Location(
        name="Arrakeen",
        requirement=noRequirement,
        effect=DeployEffect(3) + GarrisonEffect(1) + CardEffect(1) + CaptureSolariEffect(1),
        icons={Icon.SETTLEMENT}
    ),
    Location(
        name="Carthag",
        requirement=noRequirement,
        effect=DeployEffect(3) + GarrisonEffect(1) + IntrigueEffect() + CaptureSolariEffect(1),
        icons={Icon.SETTLEMENT}
    ),
    Location(
        name="Research Station",
        requirement=WaterRequirement(2),
        effect=DeployEffect(2) + CardEffect(3),
        icons={Icon.SETTLEMENT}
    ),
    Location(
        name="Sietch Tabr",
        requirement=WaterRequirement(2) + InfluenceRequirement(dc.Faction.FREMEN, 2),
        effect=DeployEffect(3) + CardEffect(3),
        icons={Icon.SETTLEMENT}
    ),

    Location(
        name="Conspire",
        requirement=SpiceRequirement(4),
        effect=InfluenceEffect(dc.Faction.EMPEROR, 1) + SolariEffect(4) + GarrisonEffect(2) + IntrigueEffect(),
        icons={Icon.EMPEROR},
        faction=Faction.EMPEROR
    ),
    Location(
        name="Wealth",
        requirement=noRequirement,
        effect=InfluenceEffect(dc.Faction.EMPEROR, 1) + SolariEffect(2),
        icons={Icon.EMPEROR},
        faction=Faction.EMPEROR
    ),

    Location(
        name="Heighliner",
        requirement=SpiceRequirement(6),
        effect=InfluenceEffect(dc.Faction.SPACING_GUILD, 1) + GarrisonEffect(5) + DeployEffect(7) + WaterEffect(2),
        icons={Icon.SPACING_GUILD},
        faction=Faction.SPACING_GUILD
    ),
    Location(
        name="Wealth",
        requirement=noRequirement,
        effect=InfluenceEffect(dc.Faction.SPACING_GUILD, 1) + FoldSpaceEffect(),
        icons={Icon.SPACING_GUILD},
        faction=Faction.SPACING_GUILD
    ),
    # Workaround for flawed effect system
    Location(
        name="Selective Breeding",
        requirement=SpiceRequirement(2),
        icons={Icon.BENE_GESSERIT},
        effect=Effect(
            effect=lambda game, card: (
                game.current_player.remove_card(card),
                InfluenceEffect(dc.Faction.BENE_GESSERIT, 1).effect(game),
                CardEffect(2).effect(game)
            ),
            choices=[Choice(
                ChoiceType.CARD,
                lambda game, card: game.current_player.is_removable_card(card)
            )]),
        faction=Faction.BENE_GESSERIT
    ),
    Location(
        name="Secrets",
        requirement=noRequirement,
        effect=InfluenceEffect(dc.Faction.BENE_GESSERIT, 1) + IntrigueEffect() + StealIntrigueEffect(),
        icons={Icon.BENE_GESSERIT},
        faction=Faction.BENE_GESSERIT
    ),

    Location(
        name="Hardy Warriors",
        requirement=WaterRequirement(1),
        effect=InfluenceEffect(dc.Faction.FREMEN, 1) + DeployEffect(4) + GarrisonEffect(2),
        icons={Icon.FREMEN},
        faction=Faction.FREMEN
    ),
    Location(
        name="Secrets",
        requirement=noRequirement,
        effect=InfluenceEffect(dc.Faction.FREMEN, 1) + DeployEffect(2) + WaterEffect(1),
        icons={Icon.FREMEN},
        faction=Faction.FREMEN
    ),
]
