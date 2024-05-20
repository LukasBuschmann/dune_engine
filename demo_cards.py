import random
from typing import Callable, List, Set

from enums import Icon, ChoiceType, Faction, IntrigueType
from Effect import Effect, swappero_effect, noEffect, ChoicelessEffect, PersuasionEffect, WaterEffect,  SpiceEffect, SolariEffect, GarrisonEffect, ForceEffect, VictoryEffect, IntrigueEffect, InfluenceChoiceEffect, CardEffect
from Requirement import Requirement, SpiceRequirement, noRequirement, Choice, BreakBinChoice
import itertools


class Card:
    def __init__(self,
                 name: str,
                 persuasion_cost: int = 0,
                 icons: Set[Icon] = set(),
                 factions: Set[Faction] = set(),
                 agent_effect: Effect = noEffect,
                 reveal_effect: Effect = noEffect,
                 removal_effect: ChoicelessEffect = noEffect,
                 acquisition_effect: ChoicelessEffect = noEffect,
                 copies: int = 1):
        self.name: str = name
        self.persuasion_cost: int = persuasion_cost
        self.icons: Set[Icon] = icons
        self.factions: Set[Faction] = factions
        self.agent_effect: Effect = agent_effect
        self.reveal_effect: Effect = reveal_effect
        self.removal_effect: ChoicelessEffect = removal_effect
        self.acquisition_effect: ChoicelessEffect = acquisition_effect
        self.copies = copies

    def __repr__(self):
        return self.name + ' ' + (str(self.icons) if len(self.icons) > 0 else '')
    def get_instances(self):
        return [
            CardInstance(i, self.name, self.persuasion_cost, self.icons, self.factions, self.agent_effect,
                         self.reveal_effect, self.removal_effect, self.acquisition_effect, self.copies)
            for i in range(self.copies)
        ]


class CardInstance:
    def __init__(self,
                 id: int,
                 name: str,
                 persuasion_cost: int = 0,
                 icons: Set[Icon] = set(),
                 factions: Set[Faction] = set(),
                 agent_effect: Effect = noEffect,
                 reveal_effect: Effect = noEffect,
                 removal_effect: Effect = noEffect,
                 acquisition_effect: Effect = noEffect,
                 copies: int = 1):
        self.name: str = name
        self.persuasion_cost: int = persuasion_cost
        self.icons: Set[Icon] = icons
        self.factions: Set[Faction] = factions
        self.agent_effect: Effect = agent_effect
        self.reveal_effect: Effect = reveal_effect
        self.removal_effect: Effect = removal_effect
        self.acquisition_effect: Effect = acquisition_effect
        self.copies = copies
        self.id = id

    def __repr__(self):
        return self.name + ' ' + (str(self.icons) if len(self.icons) > 0 else '')

shop_cards = [
    Card(
        name="Arrakis Liaison",
        persuasion_cost=2,
        icons={Icon.STATECRAFT, Icon.SETTLEMENT},
        factions={Faction.FREMEN},
        reveal_effect=ChoicelessEffect(
            effect=lambda game: game.current_player.change_persuasion(2)
        ),
        copies=10  # bs number
    ),
    Card(
        name="The Spice Must Flow",
        persuasion_cost=9,
        icons=set(),
        reveal_effect=ChoicelessEffect(
            effect=lambda game: game.current_player.change_spice(1)
        ),
        acquisition_effect=ChoicelessEffect(
            effect=lambda game: game.current_player.change_victory_points(1)
        ),
        copies=10  # bs number
    ),
]

foldspace = Card(
    name="Foldspace",
    icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN, Icon.ECONOMY, Icon.STATECRAFT, Icon.SETTLEMENT},
    agent_effect=CardEffect(1),
    copies=10
)

# ToDo: Make Ids unique among players
start_cards = [
    Card(
        name='Signet Ring',
        icons={Icon.STATECRAFT, Icon.SETTLEMENT, Icon.ECONOMY},
        reveal_effect=PersuasionEffect(1),
        copies=1
    ),
    Card(
        name='Seek Allies',
        icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN},
       agent_effect=ChoicelessEffect(lambda game: game.current_player.played_cards.remove(list(filter(lambda card: card.name == 'Seek Allies', game.current_player.played_cards))[0])),
        copies=1
    ),
    Card(
        name='Diplomacy',
        icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN},
        reveal_effect=PersuasionEffect(1),
        copies=1
    ),
    Card(
        name='Reconnaissance',
        icons={Icon.SETTLEMENT},
        reveal_effect=PersuasionEffect(1),
        copies=1
    ),
    Card(
        name='Dagger',
        icons={Icon.STATECRAFT},
        reveal_effect=ForceEffect(1),
        copies=2
    ),
    Card(
        name='Dune, the Desert Planet',
        icons={Icon.ECONOMY},
        reveal_effect=PersuasionEffect(1),
        copies=2
    ),
    Card(
        name='Convincing Argument',
        reveal_effect=PersuasionEffect(2),
        copies=2
    ),
]

cards = [
    Card(
        name="Firm Grip",
        persuasion_cost=4,
        icons={Icon.EMPEROR, Icon.STATECRAFT},
        factions={Faction.EMPEROR},
        agent_effect=Effect(
            effect=lambda game, activated, faction: (
                game.current_player.change_solari(-2),
                game.current_player.change_influence(faction, 1)
            ) if activated else None,
            choices=[
                BreakBinChoice(
                    condition=lambda game, decision: True if (
                                                                     game.current_player.solari >= 2 and game.current_player.get_changeable_factions(
                                                                 1)) or decision is False else False),
                Choice(
                    choice_type=ChoiceType.FACTION,
                    condition=lambda game,
                                     faction: True if faction in game.current_player.get_changeable_factions(
                        1).intersection(
                        {Faction.SPACING_GUILD, Faction.BENE_GESSERIT, Faction.FREMEN}) else False)
            ],
        ),
        reveal_effect=ChoicelessEffect(
            effect=lambda game: game.current_player.change_persuation(4) if game.current_player.has_alliance(
                Faction.EMPEROR) else None
        )
    ),


]

class ConflictCard:
    def __init__(self, name: str, tier: int, rewards: List[Effect]):
        self.name = name
        self.tier = tier
        self.rewards = rewards


conflict_cards = [
    # ConflictCard(
    #     name='Skirmish',
    #     tier=1,
    #     rewards=[
    #         VictoryEffect(1),
    #         WaterEffect(1),
    #         SpiceEffect(1),
    #     ]
    # ),
    # ConflictCard(
    #     name='Skirmish',
    #     tier=1,
    #     rewards=[
    #         VictoryEffect(1),
    #         IntrigueEffect() + SolariEffect(1),
    #         SolariEffect(2),
    #     ]
    # ),
    ConflictCard(
        name='Skirmish',
        tier=1,
        rewards=[
            Effect(
                effect=lambda game, faction: (
                    game.current_player.change_influence(faction, 1) if game.current_player.has_changeable_factions(1) else None,
                    game.current_player.change_solari(2)
                ),
                choices=[
                    Choice(ChoiceType.FACTION,
                           # every faction allowed, when everything is maxed
                           lambda game, faction: faction in game.current_player.get_changeable_factions(1) or not game.current_player.has_changeable_faction(1))
                ]
            ),
            SolariEffect(3),
            SolariEffect(2),
        ]
    ),
    ConflictCard(
        name='Skirmish',
        tier=1,
        rewards=[
            Effect(
                effect=lambda game, faction: (
                    game.current_player.change_influence(faction, 1) if game.current_player.has_changeable_factions(1) else None,
                    game.current_player.change_spice(1)
                ),
                choices=[
                    Choice(ChoiceType.FACTION,
                           # every faction allowed, when everything is maxed
                           lambda game, faction: faction in game.current_player.get_changeable_factions(1) or not game.current_player.has_changeable_factions(1))
                ]
            ),
            SpiceEffect(2),
            SpiceEffect(1),
        ]
    )
]


class Intrigue:
    def __init__(self, name: str, effect: Effect, requirement: Requirement = noRequirement, intrigue_type: IntrigueType = IntrigueType.PLOT, copies: int = 10):
        self.name: str = name
        self.effect: Effect = effect
        self.requirement: Requirement = requirement
        self.intrigue_type: IntrigueType = intrigue_type
        self.copies = copies

    def get_instances(self):
        return [
            IntrigueInstance(i, self.name, self.effect, self.requirement, self.intrigue_type)
            for i in range(self.copies)
        ]
    def __repr__(self):
        return self.name

class IntrigueInstance:
    def __init__(self, id: int, name: str, effect: Effect, requirement, intrigue_type: IntrigueType):
        self.name: str = name
        self.effect: Effect = effect
        self.requirement: Requirement = requirement
        self.intrigue_type: IntrigueType = intrigue_type
        self.id = id

    def __repr__(self):
        return self.name

plots = [
    Intrigue("Swappero", swappero_effect, noRequirement),
    Intrigue(
        "Dispatch an Envoy ",
        ChoicelessEffect(
            effect=lambda game: game.current_player.add_icons(
                [Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN])
        )
    ),
    Intrigue(
        name='Secrets Of The Sisterhood',
        effect=ChoicelessEffect(lambda game: game.current_player.change_influence(Faction.BENE_GESSERIT, 1)),
    ),
    Intrigue(
        name='Favored Subjects',
        effect=ChoicelessEffect(lambda game: game.current_player.change_influence(Faction.EMPEROR, 1)),
    ),
    Intrigue(
        name='Know Their Ways',
        effect=ChoicelessEffect(lambda game: game.current_player.change_influence(Faction.FREMEN, 1)),
    ),
    Intrigue(
        name='Guild Authorization',
        effect=ChoicelessEffect(lambda game: game.current_player.change_influence(Faction.SPACING_GUILD, 1)),
    ),
    Intrigue(
        name='Windfall',
        effect=ChoicelessEffect(lambda game: game.current_player.change_solari(2)),
    ),
    Intrigue(
        name='Water Peddlers Union',
        effect=ChoicelessEffect(lambda game: game.current_player.change_water(1)),
    ),
    Intrigue(
        name='Charisma',
        effect=ChoicelessEffect(lambda game: game.current_player.change_persuation(2)),
    ),
    Intrigue(
        name='Rapid Mobilization',
        effect=ChoicelessEffect(lambda game: game.current_player.change_to_deploy(game.max_troops)),
    ),
    Intrigue(
        name='Reinforcements',
        effect=Effect(
            effect=lambda game, decision: (
                game.current_player.change_solari(-3),
                game.current_player.change_garrison(3),
                game.current_player.change_to_deploy(3) if game.current_player.is_revealing_turn else None
            ) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.solari >= 3)]
        ),
    ),
    Intrigue(
        name='The Sleeper Must Awaken',
        effect=Effect(
            effect=lambda game, decision:
            (game.current_player.change_spice(-4), game.current_player.change_victory_points(1)) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.spice >= 4)]
        ),
    ),
    Intrigue(
        name='Choam Shares',
        effect=Effect(
            effect=lambda game, decision:
            (game.current_player.change_solari(-7), game.current_player.change_victory_points(1)) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.solari >= 7)]
        ),
    ),
    Intrigue(
        name='Refocus',
        effect=ChoicelessEffect(lambda game: (
            game.current_player.deck.extend(game.current_player.discard_pile),
            random.shuffle(game.current_player.deck),
            game.current_player.draw()
        )),
    ),
    Intrigue(
        name='Bribery',
        effect=Effect(
            effect=lambda game, decision, faction: (
                game.current_player.change_solari(-2),
                game.current_player.change_influence(faction, 1)
            ) if decision else None,
            choices=[
                BreakBinChoice(
                    lambda game, decision: True if not decision else game.current_player.solari >= 2,
                ),
                Choice(ChoiceType.FACTION,
                       lambda game, faction: faction in game.current_player.get_changeable_factions(1)
                       )
            ]
        ),
    ),
    Intrigue(
        name='Double Cross',
        effect=Effect(
            effect=lambda game, decision, player: (
                game.current_player.change_solari(-1),
                player.change_in_combat(-1),
                game.current_player.change_to_deploy(1)
            ) if decision else None,
            choices=[
                BreakBinChoice(
                    lambda game, decision: True if not decision else game.current_player.solari >= 1,
                ),
                Choice(ChoiceType.PLAYER,
                       lambda game, faction: faction in game.current_player.get_changeable_factions(1)
                       )
            ]
        ),
    ),
]
