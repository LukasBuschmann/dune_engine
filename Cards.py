import random
from typing import Callable, List, Set

from enums import Icon, ChoiceType, Faction, IntrigueType
from Effect import Effect, DeployEffect, noEffect, InfluenceEffect, ChoicelessEffect, PersuasionEffect, \
    WaterEffect, SpiceEffect, SolariEffect, GarrisonEffect, ForceEffect, VictoryEffect, IntrigueEffect, \
    InfluenceChoiceEffect, CardEffect, RemoveCardEffect, AgentEffect, RetreatEffect
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

    def is_playable_with(self, game: 'Game', card: 'CardInstance'):
        for location in game.locations:
            if location.is_available_with(game, card):
                return True
        return False

noCard = CardInstance(0, "no card")

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
    icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN, Icon.ECONOMY, Icon.STATECRAFT,
           Icon.SETTLEMENT},
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
        agent_effect=ChoicelessEffect(lambda game: game.current_player.played_cards.remove(
            list(filter(lambda card: card.name == 'Seek Allies', game.current_player.played_cards))[0])),
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
    Card(
        name="Missionaria Protectiva",
        persuasion_cost=1,
        icons={Icon.SETTLEMENT},
        factions={Faction.BENE_GESSERIT},
        reveal_effect=PersuasionEffect(1),
        agent_effect=InfluenceChoiceEffect(1,
                                           precondition=lambda game: game.current_player.faction_cards_in_play(
                                               Faction.BENE_GESSERIT) > 0 and game.current_player.has_changeable_factions())
    ),
    Card(
        name="Spice Smugglers",
        persuasion_cost=2,
        icons={Icon.SETTLEMENT},
        factions={Faction.SPACING_GUILD},
        reveal_effect=PersuasionEffect(1) + ForceEffect(1),
        agent_effect=Effect(
            effect=lambda game, activated: (
                SpiceEffect(-2).effect(game),
                InfluenceEffect(Faction.SPACING_GUILD, 1).effect(game),
                SolariEffect(3).effect(game)
            ) if activated else None,
            choices=[Choice(ChoiceType.BOOLEAN, lambda game, decision: True)],
            precondition=lambda game: game.current_player.spice >= 2
        ),
    ),
    Card(
        name="Gurney Halleck",
        persuasion_cost=6,
        icons={Icon.SETTLEMENT},
        agent_effect=GarrisonEffect(2) + CardEffect(1),
        reveal_effect=Effect(
            effect=lambda game, activated: (
                PersuasionEffect(2).effect(game),
                (
                    SolariEffect(-3).effect(game),
                    GarrisonEffect(2).effect(game),
                    DeployEffect(2).effect(game)
                ) if activated else None
            ),
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.solari >= 3)]
        ),
    ),
    Card(
        name="Liet Kynes",
        persuasion_cost=5,
        icons={Icon.SETTLEMENT, Icon.FREMEN},
        factions={Faction.FREMEN, Faction.EMPEROR},
        acquisition_effect=InfluenceEffect(Faction.EMPEROR, 1),
        reveal_effect=ChoicelessEffect(
            lambda game: game.current_player.change_persuasion(
                2 * (game.current_player.faction_cards_in_play(Faction.FREMEN) + 1))
        )
    ),
    Card(
        name="Sardaukar Infantry",
        persuasion_cost=1,
        factions={Faction.EMPEROR},
        reveal_effect=PersuasionEffect(1) + ForceEffect(2),
    ),
    Card(
        name="Sietch Reverend Mother",
        persuasion_cost=4,
        icons={Icon.FREMEN, Icon.BENE_GESSERIT},
        factions={Faction.BENE_GESSERIT, Faction.FREMEN},
        reveal_effect=ChoicelessEffect(
            lambda game: (
                PersuasionEffect(3).effect(game),
                SpiceEffect(1).effect(game)
            ) if game.current_player.faction_cards_in_play(Faction.BENE_GESSERIT) > 0 else None
        ),
    ),
    Card(
        name="Imperial Spy",
        persuasion_cost=2,
        icons={Icon.EMPEROR},
        factions={Faction.EMPEROR},
        reveal_effect=PersuasionEffect(1) + ForceEffect(1),
        agent_effect=Effect(
            effect=lambda game, decision: (game.current_player.played_cards.remove(
                list(filter(lambda card: card.name == 'Imperial Spy', game.current_player.played_cards))[0]),
                                           IntrigueEffect().effect(game)) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN, lambda game, decision: True)]
        )
    ),
    Card(
        name="Power Play",
        persuasion_cost=5,
        icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN},
        agent_effect=ChoicelessEffect(
            lambda game: game.current_player.change_influence(game.current_player.current_location.faction,
                                                              1) if game.current_player.current_location.faction in [
                Faction.FREMEN, Faction.BENE_GESSERIT, Faction.SPACING_GUILD, Faction.EMPEROR] else None
        )
    ),
    Card(
        name="Sardaukar Legion",
        persuasion_cost=5,
        icons={Icon.EMPEROR, Icon.STATECRAFT},
        factions={Faction.EMPEROR},
        agent_effect=GarrisonEffect(2),
        reveal_effect=PersuasionEffect(1) + DeployEffect(3)
    ),
    Card(
        name="Other Memory",
        persuasion_cost=4,
        icons={Icon.SETTLEMENT, Icon.ECONOMY},
        factions={Faction.BENE_GESSERIT},
        reveal_effect=PersuasionEffect(2),
        agent_effect=Effect(
            effect=lambda game, decision, card: (CardEffect(1).effect(game) if not decision else None,
                                                 game.current_player.draw_from_discard(card) if decision else None),
            choices=[
                BreakBinChoice(
                    lambda game, decision: True if not decision else 0 < len(list(
                        filter(lambda card: Faction.BENE_GESSERIT in card.factions,
                               game.current_player.discard_pile)))),
                Choice(
                    ChoiceType.CARD,
                    lambda game,
                           card: Faction.BENE_GESSERIT in card.factions and card in game.current_player.discard_pile)
            ]
        )
    ),
    Card(
        name="Shifting Allegiances",
        persuasion_cost=3,
        icons={Icon.STATECRAFT, Icon.ECONOMY},
        reveal_effect=PersuasionEffect(2),
        agent_effect=Effect(
            effect=lambda game, decision, donor, receiver: (
                InfluenceEffect(donor, -1).effect(game),
                SpiceEffect(-2).effect(game),
                InfluenceEffect(receiver, 2).effect(game),
            ) if decision else None,
            choices=[
                BreakBinChoice(lambda game, decision: True if game.current_player.spice >= 2 else False),
                Choice(ChoiceType.FACTION,
                       lambda game, faction: faction in game.current_player.get_changeable_factions(-1)),
                Choice(ChoiceType.FACTION,
                       lambda game, faction: faction in game.current_player.get_changeable_factions(2)),
            ]
        )
    ),
    Card(
        name="Duncan Idaho",
        persuasion_cost=4,
        icons={Icon.SETTLEMENT},
        reveal_effect=WaterEffect(1) + ForceEffect(2),
        agent_effect=Effect(
            effect=lambda game, decision: (WaterEffect(-1), GarrisonEffect(1), CardEffect(1)) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.water >= 1)]
        )
    ),
    Card(
        name="Piter De Vries",
        persuasion_cost=5,
        icons={Icon.SETTLEMENT, Icon.STATECRAFT},
        agent_effect=IntrigueEffect(),
        reveal_effect=PersuasionEffect(3) + ForceEffect(1),
    ),
    Card(
        name="Worm Riders",
        persuasion_cost=6,
        icons={Icon.SETTLEMENT, Icon.ECONOMY},
        factions={Faction.FREMEN},
        agent_effect=SpiceEffect(2),
        reveal_effect=ChoicelessEffect(
            lambda game: (
                game.current_player.change_force(4) if game.current_player.factions[Faction.FREMEN][
                                                           'influence'] >= 2 else None,
                game.current_player.change_force(2) if game.current_player.has_alliance(Faction.FREMEN) else None
            )
        )
    ),
    Card(
        name="Space Travel",
        persuasion_cost=3,
        icons={Icon.SPACING_GUILD},
        factions={Faction.SPACING_GUILD},
        reveal_effect=PersuasionEffect(2),
        agent_effect=CardEffect(1),
    ),
    Card(
        name="Thufir Hawat",
        persuasion_cost=5,
        icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.FREMEN, Icon.BENE_GESSERIT, Icon.SPACING_GUILD, Icon.EMPEROR},
        agent_effect=CardEffect(1),
        reveal_effect=PersuasionEffect(1) + IntrigueEffect(),
    ),
    Card(
        name="Lady Jessica",
        persuasion_cost=7,
        icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.STATECRAFT, Icon.BENE_GESSERIT},
        factions={Faction.BENE_GESSERIT},
        acquisition_effect=InfluenceEffect(Faction.BENE_GESSERIT, 1),  # ToDo: This should be a faction choice
        agent_effect=CardEffect(2),
        reveal_effect=PersuasionEffect(3) + ForceEffect(1),
    ),
    Card(
        name="Smuggler's Thopter",
        persuasion_cost=4,
        icons={Icon.ECONOMY},
        factions={Faction.SPACING_GUILD},
        agent_effect=ChoicelessEffect(
            lambda game: CardEffect(2).effect(game) if game.current_player.factions[Faction.SPACING_GUILD][
                                                           'influence'] >= 2 else None
        ),
        reveal_effect=PersuasionEffect(1) + SpiceEffect(1),
    ),
    Card(
        name="Test of Humanity",
        persuasion_cost=3,
        icons={Icon.SETTLEMENT, Icon.STATECRAFT, Icon.BENE_GESSERIT},
        factions={Faction.BENE_GESSERIT},
        reveal_effect=PersuasionEffect(2),
        agent_effect=ChoicelessEffect(
            lambda game: [player.change_in_combat(-1) for player in game.players if player is not game.current_player]
            # ToDo: this should be a choice retreat or discard
        )
    ),
    Card(
        name="Stilgar",
        persuasion_cost=5,
        icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.FREMEN},
        factions={Faction.FREMEN},
        agent_effect=WaterEffect(1),
        reveal_effect=PersuasionEffect(2) + ForceEffect(3),
    ),
    Card(
        name="Guild Bankers",
        persuasion_cost=3,
        icons={Icon.STATECRAFT, Icon.SPACING_GUILD, Icon.EMPEROR},
        factions={Faction.SPACING_GUILD},
        reveal_effect=PersuasionEffect(3),  # ToDo: This should make Spice must Flow less expensive
    ),
    Card(
        name="Spice Hunter",
        persuasion_cost=2,
        icons={Icon.ECONOMY, Icon.FREMEN},
        factions={Faction.FREMEN},
        reveal_effect=ChoicelessEffect(
            lambda game: ((PersuasionEffect(1) + ForceEffect(1)).effect(game),
                          SpiceEffect(1).effect(game) if game.current_player.faction_cards_in_play(
                              Faction.FREMEN) > 0 else None)
        ),
    ),
    Card(
        name="Fedaykin Death Commando",
        persuasion_cost=3,
        icons={Icon.SETTLEMENT, Icon.ECONOMY},
        factions={Faction.FREMEN},
        agent_effect=RemoveCardEffect(),
        reveal_effect=ChoicelessEffect(
            lambda game: (
                PersuasionEffect(1).effect(game),
                ForceEffect(3).effect(game) if game.current_player.faction_cards_in_play(
                    Faction.FREMEN) > 0 else None)
        ),
    ),
    Card(
        name="Opulence",
        persuasion_cost=6,
        icons={Icon.EMPEROR},
        factions={Faction.EMPEROR},
        agent_effect=SolariEffect(3),
        reveal_effect=Effect(
            effect=lambda game, decision: (
                PersuasionEffect(1).effect(game),
                (SolariEffect(-6).effect(game), VictoryEffect(1).effect(game)) if decision else None
            ),
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.solari >= 6)]
        ),
    ),
    Card(
        name="Kwisatz Haderach",
        persuasion_cost=8,
        icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.STATECRAFT, Icon.BENE_GESSERIT, Icon.FREMEN, Icon.SPACING_GUILD,
               Icon.EMPEROR},
        agent_effect=CardEffect(1) + AgentEffect(),  # ToDo: This should be a lot more ccmplex
    ),
    Card(
        name="Guild Ambassador",
        persuasion_cost=4,
        icons={Icon.STATECRAFT},
        factions={Faction.SPACING_GUILD},
        agent_effect=Effect(
            effect=lambda game, decision: (InfluenceEffect(Faction.SPACING_GUILD, 1).effect(game) if decision else None,
                                           SpiceEffect(2).effect(game) if not decision else None),
            choices=[Choice(ChoiceType.BOOLEAN, lambda game, decision: True)]
        ),
        reveal_effect=Effect(
            effect=lambda game, decision: (
                SpiceEffect(-3).effect(game), VictoryEffect(1).effect(game)) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.spice >= 3)]
        ),
    ),
    Card(
        name="Gene Manipulation",
        persuasion_cost=3,
        icons={Icon.SETTLEMENT, Icon.STATECRAFT},
        factions={Faction.BENE_GESSERIT},
        agent_effect=Effect(
            effect=lambda game, card: (game.current_player.remove_card(card),
                                       SpiceEffect(2).effect(game) if game.current_player.faction_cards_in_play(
                                           Faction.BENE_GESSERIT) > 0 else None),
            choices=[Choice(
                ChoiceType.CARD,
                lambda game, card: game.current_player.is_removable_card(card))]
        ),
        reveal_effect=PersuasionEffect(2),
    ),
    Card(
        name="Dr. Yueh",
        persuasion_cost=1,
        icons={Icon.SETTLEMENT},
        agent_effect=CardEffect(1),
        reveal_effect=PersuasionEffect(1),
    ),
    Card(
        name="Fremen Camp",
        persuasion_cost=4,
        icons={Icon.ECONOMY},
        factions={Faction.FREMEN},
        reveal_effect=PersuasionEffect(2) + ForceEffect(1),
        agent_effect=Effect(
            effect=lambda game, decision: (
                SpiceEffect(-2).effect(game), GarrisonEffect(3).effect(game)) if decision else None,
            choices=[Choice(ChoiceType.BOOLEAN,
                            lambda game, decision: True if not decision else game.current_player.spice >= 2)]
        )
    ),
    Card(
        name="Chani",
        persuasion_cost=5,
        icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.FREMEN},
        factions={Faction.FREMEN},
        acquisition_effect=WaterEffect(1),
        reveal_effect=PersuasionEffect(2) + RetreatEffect(12),
    ),
    Card(
        name="Crysknife",
        persuasion_cost=3,
        icons={Icon.ECONOMY, Icon.FREMEN},
        factions={Faction.FREMEN},
        agent_effect=SolariEffect(1),
        reveal_effect=ChoicelessEffect(
            lambda game: (
                ForceEffect(1).effect(game),
                InfluenceEffect(Faction.FREMEN, 1).effect(game) if game.current_player.faction_cards_in_play(
                    Faction.FREMEN) > 0 else None
            )
        ),
    ),
    Card(
        name="Choam Dictatorship",
        persuasion_cost=8,
        acquisition_effect=InfluenceEffect(Faction.EMPEROR, 1)
                           + InfluenceEffect(Faction.SPACING_GUILD, 1)
                           + InfluenceEffect(Faction.BENE_GESSERIT, 1)
                           + InfluenceEffect(Faction.FREMEN, 1),
        reveal_effect=SolariEffect(3)
    ),
    Card(
        name="Carryall",
        persuasion_cost=5,
        icons={Icon.ECONOMY},
        reveal_effect=PersuasionEffect(1) + SpiceEffect(1),
        agent_effect=ChoicelessEffect(
            lambda game: (
                SpiceEffect(1).effect(game) if game.current_player.current_location.name == "Imperial Basin" else None,
                SpiceEffect(2).effect(game) if game.current_player.current_location.name == "Hagga Basin" else None,
                SpiceEffect(3).effect(game) if game.current_player.current_location.name == "The Great Flat" else None,
            )
        )
    ),
    Card(
        name="Bene Gesserit Sister",
        persuasion_cost=3,
        icons={Icon.STATECRAFT, Icon.BENE_GESSERIT},
        factions={Faction.BENE_GESSERIT},
        reveal_effect=Effect(
            effect=lambda game, decision: (PersuasionEffect(2).effect(game) if decision else None,
                                           ForceEffect(2).effect(game) if not decision else None),
            choices=[Choice(ChoiceType.BOOLEAN, lambda game, decision: True)]
        )
    ),
    Card(
        name="Bene Gesserit Initiate",
        persuasion_cost=3,
        icons={Icon.ECONOMY, Icon.SETTLEMENT, Icon.STATECRAFT},
        factions={Faction.BENE_GESSERIT},
        agent_effect=CardEffect(1),
        reveal_effect=PersuasionEffect(1),
    ),
    Card(
        name="Arrakis Recruiter",
        persuasion_cost=2,
        icons={Icon.SETTLEMENT},
        agent_effect=GarrisonEffect(1),
        reveal_effect=PersuasionEffect(1) + ForceEffect(1),
    ),
    Card(
        name="Assassination Mission",
        persuasion_cost=1,
        reveal_effect=SolariEffect(1) + ForceEffect(1),
        removal_effect=SolariEffect(4),
    ),
    Card(
        name="Scout",
        persuasion_cost=1,
        icons={Icon.SETTLEMENT, Icon.ECONOMY},
        reveal_effect=PersuasionEffect(1) + ForceEffect(1) + RetreatEffect(2),
    ),
    Card(
        name="The Voice",
        persuasion_cost=2,
        icons={Icon.SETTLEMENT, Icon.ECONOMY},
        factions={Faction.BENE_GESSERIT},
        reveal_effect=PersuasionEffect(2),
        agent_effect=Effect(
            effect=lambda game, location: location.occupy(),
            choices=[Choice(ChoiceType.LOCATION, lambda game, location: True)]  # ToDo: This should work differently
        )
    ),
    Card(
        name="Guild Administrator",
        persuasion_cost=2,
        icons={Icon.SPACING_GUILD, Icon.ECONOMY},
        factions={Faction.SPACING_GUILD},
        agent_effect=RemoveCardEffect(),
        reveal_effect=PersuasionEffect(1),
    ),
    Card(
        name="Gun Thopter",
        persuasion_cost=4,
        icons={Icon.SETTLEMENT, Icon.ECONOMY},
        agent_effect=ChoicelessEffect(
            lambda game: [player.change_garrison(-1) for player in game.players if player is not game.current_player]
        )
    )

]


class ConflictCard:
    def __init__(self, name: str, tier: int, rewards: List[Effect]):
        self.name = name
        self.tier = tier
        self.rewards = rewards

    def __repr__(self):
        return f"{self.name} (Tier {self.tier})\t\t{self.rewards}"


conflict_cards = [
    ConflictCard(
        name='Skirmish I',
        tier=1,
        rewards=[
            VictoryEffect(1),
            WaterEffect(1),
            SpiceEffect(1),
        ]
    ),
    ConflictCard(
        name='Skirmish II',
        tier=1,
        rewards=[
            VictoryEffect(1),
            IntrigueEffect() + SolariEffect(1),
            SolariEffect(2),
        ]
    ),
    ConflictCard(
        name='Skirmish III',
        tier=1,
        rewards=[
            Effect(
                effect=lambda game, faction: (
                    game.current_player.change_influence(faction,
                                                         1) if game.current_player.has_changeable_factions() else None,
                    game.current_player.change_solari(2)
                ),
                choices=[
                    Choice(ChoiceType.FACTION,
                           # every faction allowed, when everything is maxed
                           lambda game, faction: faction in game.current_player.get_changeable_factions(
                               1) or not game.current_player.has_changeable_factions())
                ]
            ),
            SolariEffect(3),
            SolariEffect(2),
        ]
    ),
    ConflictCard(
        name='Skirmish IV',
        tier=1,
        rewards=[
            Effect(
                effect=lambda game, faction: (
                    game.current_player.change_influence(faction,
                                                         1) if game.current_player.has_changeable_factions() else None,
                    game.current_player.change_spice(1)
                ),
                choices=[
                    Choice(ChoiceType.FACTION,
                           # every faction allowed, when everything is maxed
                           lambda game, faction: faction in game.current_player.get_changeable_factions(
                               1) or not game.current_player.has_changeable_factions())
                ]
            ),
            SpiceEffect(2),
            SpiceEffect(1),
        ]
    ),

]


class Intrigue:
    def __init__(self, name: str, effect: Effect, requirement: Requirement = noRequirement,
                 intrigue_type: IntrigueType = IntrigueType.PLOT, copies: int = 10):
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

    def is_playable(self, game: 'Game'):
        return self.requirement.is_met(game)
    def __repr__(self):
        return self.name

noIntrigue = Intrigue("no Intrigue", noEffect)

plots = [
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
