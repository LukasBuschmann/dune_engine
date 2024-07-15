from typing import Dict

from Requirement import *
from effect_functions import *


class Location:
    def __init__(self,
                 name: str,
                 requirement: 'Requirement',
                 effect: Callable[['Player'], Any],
                 icons: Set[Icon],
                 faction: Faction = None):
        self.name: str = name
        self.requirement: 'Requirement' = requirement
        self.effect: Callable[['Player'], Any] = effect
        # for agents
        self.occupied_by: List['Player'] = []
        self.icons: Set[Icon] = icons
        self.faction: Faction = faction

        self.voiced: bool = False

    def occupy(self, player: 'Player'):
        self.occupied_by.append(player)

    def clear(self):
        self.occupied_by = []
        self.voiced = False

    def is_available_with(self, player: 'Player', card: 'CardInstance'):
        if self.icons.intersection(card.icons):
            if (not self.occupied_by) or player.infiltrate:
                if self.requirement.is_met(player):
                    if not (self.voiced and player.voice):
                        return True
        return False

    def __repr__(self):
        return self.name.lower() if self.occupied_by else self.name.upper()

    def __str__(self):
        return self.name + (str(self.icons) if len(self.icons) > 0 else "")


class SpiceCollectingLocation(Location):
    def __init__(self, name: str, requirement: 'Requirement', effect: Callable[['Player'], Any], icons: Set[Icon],
                 faction: Faction = None):
        super().__init__(name, requirement, effect, icons, faction)
        self.collected_spice = 0

    def occupy(self, player: 'Player'):
        player.change_spice(self.collected_spice)
        self.collected_spice = 0
        self.occupied_by.append(player)


class CaptureLocation(Location):
    def __init__(self, name: str, requirement: 'Requirement', effect: Callable[['Player'], Any],
                 capture_effect: Callable[['Player'], Any], icons: Set[Icon],
                 faction: Faction = None):
        super().__init__(name, requirement, effect, icons, faction)
        self.captured_by = None
        self.capture_effect = capture_effect

    def occupy(self, player: 'Player'):
        if self.captured_by:
            self.capture_effect(self.captured_by)
        self.occupied_by.append(player)


class SpiceCollectingCaptureLocation(CaptureLocation, SpiceCollectingLocation):
    def __init__(self, name: str, requirement: 'Requirement', effect: Callable[['Player'], Any],
                 capture_effect: Callable[['Player'], Any], icons: Set[Icon],
                 faction: Faction = None):
        super().__init__(name, requirement, effect, capture_effect, icons, faction)
        self.collected_spice = 0

    def occupy(self, player: 'Player'):
        player.change_spice(self.collected_spice)
        self.collected_spice = 0
        if self.captured_by:
            self.capture_effect(self.captured_by)
        self.occupied_by.append(player)


faction_rewards: Dict[Faction, Callable[['Player'], Any]] = {
    Faction.EMPEROR: garrison_2,
    Faction.SPACING_GUILD: solari_3,
    Faction.BENE_GESSERIT: draw_intrigue,
    Faction.FREMEN: water_1,
}

no_location = Location(
    name=LocationName.NO_LOCATION.value,
    requirement=no_requirement,
    effect=no_effect,
    icons=set()
)

# for choice of kwisatz haderach
agent_reserves = Location(
    name=LocationName.AGENT_RESERVES.value,
    requirement=no_requirement,
    effect=no_effect,
    icons=set()
)

imperial_basin = SpiceCollectingCaptureLocation(
    name=LocationName.IMPERIAL_BASIN.value,
    requirement=no_requirement,
    effect=lambda player: (spice_1(player), enter_combat(player)),
    capture_effect=spice_1,
    icons={Icon.ECONOMY},
)
hagga_basin = SpiceCollectingLocation(
    name=LocationName.HAGGA_BASIN.value,
    requirement=water_requirement(1),
    effect=lambda player: (spice_2(player), enter_combat(player)),
    icons={Icon.ECONOMY},
)
the_great_flat = SpiceCollectingLocation(
    name=LocationName.THE_GREAT_FLAT.value,
    requirement=water_requirement(2),
    effect=lambda player: (spice_3(player), enter_combat(player)),
    icons={Icon.ECONOMY},
)
sell_melange = Location(
    name="Sell Melange",
    requirement=spice_requirement(2),
    effect=sell_melange,
    icons={Icon.ECONOMY}
)
secure_contract = Location(
    name="Secure Contract",
    requirement=no_requirement,
    effect=solari_3,
    icons={Icon.ECONOMY}
)

hall_of_oratory = Location(
    name="Hall Of Oratory",
    requirement=no_requirement,
    effect=lambda player: (garrison_1(player), persuasion_1(player)),
    icons={Icon.STATECRAFT}
)
swordmaster = Location(
    name="Swordmaster",
    requirement=solari_requirement(8) + no_sword_master_requirement,
    effect=swordmaster,
    icons={Icon.STATECRAFT}
)
rally_troops = Location(
    name="Rally Troops",
    requirement=solari_requirement(4),
    effect=garrison_4,
    icons={Icon.STATECRAFT}
)
mentat = Location(
    name="Mentat",
    requirement=solari_requirement(2),
    effect=mentat,
    icons={Icon.STATECRAFT}
)
high_council = Location(
    name="High Council",
    requirement=solari_requirement(5) + not_in_high_council_requirement,
    effect=high_council,
    icons={Icon.STATECRAFT}
)

arrakeen = CaptureLocation(
    name="Arrakeen",
    requirement=no_requirement,
    effect=lambda player: (enter_combat(player), garrison_1(player), draw_card_1(player)),
    capture_effect=solari_1,
    icons={Icon.SETTLEMENT}
)
carthag = CaptureLocation(
    name="Carthag",
    requirement=no_requirement,
    effect=lambda player: (enter_combat(player), garrison_1(player), draw_intrigue(player)),
    capture_effect=solari_1,
    icons={Icon.SETTLEMENT}
)
research_station = Location(
    name="Research Station",
    requirement=water_requirement(2),
    effect=lambda player: (enter_combat(player), draw_card_3(player)),
    icons={Icon.SETTLEMENT}
)
sietch_tabr = Location(
    name="Sietch Tabr",
    requirement=water_requirement(2) + influence_requirement(Faction.FREMEN, 2),
    effect=lambda player: (enter_combat(player), garrison_1(player), water_1(player)),
    icons={Icon.SETTLEMENT}
)

conspire = Location(
    name="Conspire",
    requirement=spice_requirement(4),
    effect=lambda player: (influence_emperor_1(player), draw_intrigue(player), garrison_2(player), solari_5(player)),
    icons={Icon.EMPEROR},
    faction=Faction.EMPEROR
)
wealth = Location(
    name="Wealth",
    requirement=no_requirement,
    effect=lambda player: (influence_emperor_1(player), solari_2(player)),
    icons={Icon.EMPEROR},
    faction=Faction.EMPEROR
)

heighliner = Location(
    name="Heighliner",
    requirement=spice_requirement(6),
    effect=lambda player: (
    influence_spacing_guild_1(player), enter_combat(player), garrison_5(player), water_2(player)),
    icons={Icon.SPACING_GUILD},
    faction=Faction.SPACING_GUILD
)
fold_space = Location(
    name="Foldspace",
    requirement=no_requirement,
    effect=lambda player: (influence_spacing_guild_1(player), fold_space(player)),
    icons={Icon.SPACING_GUILD},
    faction=Faction.SPACING_GUILD
)
selective_breading = Location(
    name="Selective Breeding",
    requirement=spice_requirement(2),
    icons={Icon.BENE_GESSERIT},
    effect=lambda player: (influence_bene_gesserit_1(player), draw_card_2(player), remove_card(player)),
    faction=Faction.BENE_GESSERIT
)
secrets = Location(
    name="Secrets",
    requirement=no_requirement,
    effect=lambda player: (influence_bene_gesserit_1(player), draw_intrigue(player), steal_intrigue(player)),
    icons={Icon.BENE_GESSERIT},
    faction=Faction.BENE_GESSERIT
)

hardy_warriors = Location(
    name="Hardy Warriors",
    requirement=water_requirement(1),
    effect=lambda player: (influence_fremen_1(player), enter_combat(player), garrison_2(player)),
    icons={Icon.FREMEN},
    faction=Faction.FREMEN
)
stillsuits = Location(
    name="Stillsuits",
    requirement=no_requirement,
    effect=lambda player: (influence_fremen_1(player), enter_combat(player), water_1(player)),
    icons={Icon.FREMEN},
    faction=Faction.FREMEN
)

locations = [
    agent_reserves,
    imperial_basin,
    hagga_basin,
    the_great_flat,
    sell_melange,
    secure_contract,
    hall_of_oratory,
    swordmaster,
    rally_troops,
    mentat,
    high_council,
    arrakeen,
    carthag,
    research_station,
    sietch_tabr,
    conspire,
    wealth,
    heighliner,
    fold_space,
    selective_breading,
    secrets,
    hardy_warriors,
    stillsuits,
]
