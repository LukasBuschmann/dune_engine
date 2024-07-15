from typing import Any

from Location import imperial_basin, arrakeen, carthag, CaptureLocation
from effect_functions import *


class Card:
    def __init__(self,
                 name: str,
                 persuasion_cost: int = 0,
                 icons=None,
                 factions=None,
                 agent_effect: Callable[['Player'], Any] = no_effect,
                 reveal_effect: Callable[['Player'], Any] = no_effect,
                 removal_effect: Callable[['Player'], Any] = no_effect,
                 acquisition_effect: Callable[['Player'], Any] = no_effect,
                 copies: int = 1):
        if factions is None:
            factions = set()
        if icons is None:
            icons = set()
        self.name: str = name
        self.persuasion_cost: int = persuasion_cost
        self.icons: Set[Icon] = icons
        self.factions: Set[Faction] = factions
        self.agent_effect: Callable[['Player'], Any] = agent_effect
        self.reveal_effect: Callable[['Player'], Any] = reveal_effect
        self.removal_effect: Callable[['Player'], Any] = removal_effect
        self.acquisition_effect: Callable[['Player'], Any] = acquisition_effect
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
                 persuasion_cost: int,
                 icons: Set[Icon],
                 factions: Set[Faction],
                 agent_effect: Callable[['Player'], Any],
                 reveal_effect: Callable[['Player'], Any],
                 removal_effect: Callable[['Player'], Any],
                 acquisition_effect: Callable[['Player'], Any],
                 copies: int = 1):
        self.name: str = name
        self.persuasion_cost: int = persuasion_cost
        self.icons: Set[Icon] = icons
        self.factions: Set[Faction] = factions
        self.agent_effect: Callable[['Player'], Any] = agent_effect
        self.reveal_effect: Callable[['Player'], Any] = reveal_effect
        self.removal_effect: Callable[['Player'], Any] = removal_effect
        self.acquisition_effect: Callable[['Player'], Any] = acquisition_effect
        self.copies = copies
        self.id = id

    def __repr__(self):
        return self.name + ' ' + (str(self.icons) if len(self.icons) > 0 else '')

    def is_playable(self, player: 'Player', card: 'CardInstance'):
        for location in player.game.locations:
            if location.is_available_with(player, card):
                return True
        return False


no_card = CardInstance(0, "no card", 0, set(), set(), no_effect, no_effect, no_effect, no_effect,
                       0)

arrakis_liaison = Card(
    name="Arrakis Liaison",
    persuasion_cost=2,
    icons={Icon.STATECRAFT, Icon.SETTLEMENT},
    factions={Faction.FREMEN},
    reveal_effect=persuasion_2,
    copies=10  # bs number
),

the_spice_must_flow = Card(
    name=CardName.THE_SPICE_MUST_FLOW.value,
    persuasion_cost=9,
    icons=set(),
    reveal_effect=spice_1,
    acquisition_effect=victory_point_1,
    copies=10  # bs number
),
shop_cards = [arrakis_liaison, the_spice_must_flow]

foldspace = Card(
    name="Foldspace",
    icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN, Icon.ECONOMY, Icon.STATECRAFT,
           Icon.SETTLEMENT},
    agent_effect=draw_card_1,
    copies=10
)

# ToDo: Implement Abilities
signet_ring = Card(
    name='Signet Ring',
    icons={Icon.STATECRAFT, Icon.SETTLEMENT, Icon.ECONOMY},
    reveal_effect=persuasion_1,
    copies=1
)
seek_allies = Card(
    name=CardName.SEEK_ALLIES.name,
    icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN},
    agent_effect=seek_allies_agent,
    copies=1
)
diplomacy = Card(
    name='Diplomacy',
    icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN},
    reveal_effect=persuasion_1,
    copies=1
)
reconnaissance = Card(
    name='Reconnaissance',
    icons={Icon.SETTLEMENT},
    reveal_effect=persuasion_1,
    copies=1
)
dagger = Card(
    name='Dagger',
    icons={Icon.STATECRAFT},
    reveal_effect=force_1,
    copies=2
)
dune = Card(
    name='Dune, the Desert Planet',
    icons={Icon.ECONOMY},
    reveal_effect=persuasion_1,
    copies=2
)
convincing_argument = Card(
    name='Convincing Argument',
    reveal_effect=persuasion_2,
    copies=2
)
# ToDo: Make Ids unique among players
start_cards = [
    signet_ring,
    seek_allies,
    diplomacy,
    reconnaissance,
    dagger,
    dune,
    convincing_argument
]

firm_grip = Card(
    name="Firm Grip",
    persuasion_cost=4,
    icons={Icon.EMPEROR, Icon.STATECRAFT},
    factions={Faction.EMPEROR},
    agent_effect=firm_grip_agent,
    reveal_effect=firm_grip_reveal,
)
missionaria_protectiva = Card(
    name="Missionaria Protectiva",
    persuasion_cost=1,
    icons={Icon.SETTLEMENT},
    factions={Faction.BENE_GESSERIT},
    reveal_effect=persuasion_1,
    # 2, since there needs to be another card except this one  in play
    agent_effect=missionaria_protectiva_agent,
)
spice_smugglers = Card(
    name="Spice Smugglers",
    persuasion_cost=2,
    icons={Icon.SETTLEMENT},
    factions={Faction.SPACING_GUILD},
    agent_effect=spice_smugglers_agent,
    reveal_effect=lambda player: (persuasion_1(player), force_1(player)),
)
gurney_halleck = Card(
    name="Gurney Halleck",
    persuasion_cost=6,
    icons={Icon.SETTLEMENT},
    agent_effect=lambda player: (garrison_2(player), draw_card_1(player)),
    reveal_effect=gurney_halleck_reveal,
)
liet_kynes = Card(
    name="Liet Kynes",
    persuasion_cost=5,
    icons={Icon.SETTLEMENT, Icon.FREMEN},
    factions={Faction.FREMEN, Faction.EMPEROR},
    acquisition_effect=influence_emperor_1,
    reveal_effect=liet_kynes_reveal
)
sardaukar_infantry = Card(
    name="Sardaukar Infantry",
    persuasion_cost=1,
    factions={Faction.EMPEROR},
    reveal_effect=lambda player: (persuasion_1, force_2),
)
sietch_reverend_mother = Card(
    name="Sietch Reverend Mother",
    persuasion_cost=4,
    icons={Icon.FREMEN, Icon.BENE_GESSERIT},
    factions={Faction.BENE_GESSERIT, Faction.FREMEN},
    agent_effect=remove_card,
    reveal_effect=sietch_reverend_mother_reveal
    # ToDo: RESTRICTION activating a fremen bond after revealing (using plot) is not possible
)
imperial_spy = Card(
    name=CardName.IMPERIAL_SPY.name,
    persuasion_cost=2,
    icons={Icon.EMPEROR},
    factions={Faction.EMPEROR},
    agent_effect=imerial_spy_agent,
    reveal_effect=lambda player: (persuasion_1(player), force_1(player)),
)
power_play = Card(
    name=CardName.POWER_PLAY.name,
    persuasion_cost=5,
    icons={Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN},
    agent_effect=power_play_agent
)
sardaukar_legion = Card(
    name="Sardaukar Legion",
    persuasion_cost=5,
    icons={Icon.EMPEROR, Icon.STATECRAFT},
    factions={Faction.EMPEROR},
    agent_effect=garrison_2,
    reveal_effect=lambda player: (persuasion_1(player), force_3(player)),
)
other_memory = Card(
    name="Other Memory",
    persuasion_cost=4,
    icons={Icon.SETTLEMENT, Icon.ECONOMY},
    factions={Faction.BENE_GESSERIT},
    agent_effect=other_memory_agent,
    reveal_effect=persuasion_2,
)
shifting_allegiances = Card(
    name="Shifting Allegiances",
    persuasion_cost=3,
    icons={Icon.STATECRAFT, Icon.ECONOMY},
    reveal_effect=persuasion_2,
    agent_effect=shifting_allegiances_agent
)
duncan_idaho = Card(
    name="Duncan Idaho",
    persuasion_cost=4,
    icons={Icon.SETTLEMENT},
    agent_effect=duncan_idaho_agent,
    reveal_effect=lambda player: (water_1(player), force_2(player)),
)
piter_de_vries = Card(
    name="Piter De Vries",
    persuasion_cost=5,
    icons={Icon.SETTLEMENT, Icon.STATECRAFT},
    agent_effect=draw_intrigue,
    reveal_effect=lambda player: (persuasion_3(player), force_1(player)),
)
worm_riders = Card(
    name="Worm Riders",
    persuasion_cost=6,
    icons={Icon.SETTLEMENT, Icon.ECONOMY},
    factions={Faction.FREMEN},
    agent_effect=spice_2,
    reveal_effect=worm_riders_reveal
)
space_travel = Card(
    name="Space Travel",
    persuasion_cost=3,
    icons={Icon.SPACING_GUILD},
    factions={Faction.SPACING_GUILD},
    agent_effect=draw_card_1,
    reveal_effect=persuasion_2,
)
thufir_hawat = Card(
    name="Thufir Hawat",
    persuasion_cost=5,
    icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.FREMEN, Icon.BENE_GESSERIT, Icon.SPACING_GUILD, Icon.EMPEROR},
    agent_effect=draw_card_1,
    reveal_effect=lambda player: (persuasion_1(player), draw_intrigue(player)),
)
lady_jessica = Card(
    name="Lady Jessica",
    persuasion_cost=7,
    icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.STATECRAFT, Icon.BENE_GESSERIT},
    factions={Faction.BENE_GESSERIT},
    acquisition_effect=choose_influence_1,
    agent_effect=draw_card_2,
    reveal_effect=lambda player: (persuasion_3(player), force_1(player)),
)
smugglers_thopter = Card(
    name="Smuggler's Thopter",
    persuasion_cost=4,
    icons={Icon.ECONOMY},
    factions={Faction.SPACING_GUILD},
    agent_effect=smugglers_thopter_agent,
    reveal_effect=lambda player: (persuasion_1(player), spice_1(player)),
)
test_of_humanity_agent = Card(
    name="Test of Humanity",
    persuasion_cost=3,
    icons={Icon.SETTLEMENT, Icon.STATECRAFT, Icon.BENE_GESSERIT},
    factions={Faction.BENE_GESSERIT},
    reveal_effect=persuasion_2,
    agent_effect=test_of_humanity_agent
)
stilgar = Card(
    name="Stilgar",
    persuasion_cost=5,
    icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.FREMEN},
    factions={Faction.FREMEN},
    agent_effect=water_1,
    reveal_effect=lambda player: (persuasion_2(player), force_3(player)),
)
guild_bankers = Card(
    name="Guild Bankers",
    persuasion_cost=3,
    icons={Icon.STATECRAFT, Icon.SPACING_GUILD, Icon.EMPEROR},
    factions={Faction.SPACING_GUILD},
    reveal_effect=guild_bankers_reveal
)
spice_hunter = Card(
    name="Spice Hunter",
    persuasion_cost=2,
    icons={Icon.ECONOMY, Icon.FREMEN},
    factions={Faction.FREMEN},
    reveal_effect=spice_hunter_reveal,
)
fedaykin_death_commando = Card(
    name="Fedaykin Death Commando",
    persuasion_cost=3,
    icons={Icon.SETTLEMENT, Icon.ECONOMY},
    factions={Faction.FREMEN},
    agent_effect=remove_card,
    reveal_effect=fedaykin_death_commando_reveal,
)
opulence = Card(
    name="Opulence",
    persuasion_cost=6,
    icons={Icon.EMPEROR},
    factions={Faction.EMPEROR},
    agent_effect=solari_3,
    reveal_effect=opulence_reveal,
)
kwisatz_haderach = Card(
    name="Kwisatz Haderach",
    persuasion_cost=8,
    icons=set(),
    agent_effect=kwisatz_haderach_agent
)
guild_ambassador = Card(
    name="Guild Ambassador",
    persuasion_cost=4,
    icons={Icon.STATECRAFT},
    factions={Faction.SPACING_GUILD},
    agent_effect=guild_ambassador_agent,
    reveal_effect=guild_bankers_reveal,
)
gene_manipulation = Card(
    name="Gene Manipulation",
    persuasion_cost=3,
    icons={Icon.SETTLEMENT, Icon.STATECRAFT},
    factions={Faction.BENE_GESSERIT},
    agent_effect=gene_manipulation_agent,
    reveal_effect=persuasion_2,
)
dr_yueh = Card(
    name="Dr. Yueh",
    persuasion_cost=1,
    icons={Icon.SETTLEMENT},
    agent_effect=draw_card_1,
    reveal_effect=persuasion_1,
)
fremen_camp = Card(
    name="Fremen Camp",
    persuasion_cost=4,
    icons={Icon.ECONOMY},
    factions={Faction.FREMEN},
    agent_effect=fremen_camp_agent,
    reveal_effect=lambda player: (persuasion_2(player), force_1(player)),
)
chani = Card(
    name="Chani",
    persuasion_cost=5,
    icons={Icon.SETTLEMENT, Icon.ECONOMY, Icon.FREMEN},
    factions={Faction.FREMEN},
    acquisition_effect=water_1,
    reveal_effect=lambda player: (persuasion_2(player), retreat_all(player)),
)
crysknife = Card(
    name="Crysknife",
    persuasion_cost=3,
    icons={Icon.ECONOMY, Icon.FREMEN},
    factions={Faction.FREMEN},
    agent_effect=solari_1,
    reveal_effect=crysknife_reveal,
)
choam_directorship = Card(
    name="Choam Directorship",
    persuasion_cost=8,
    acquisition_effect=lambda player: (
        influence_emperor_1(player),
        influence_spacing_guild_1(player),
        influence_bene_gesserit_1(player),
        influence_fremen_1(player),
    ),
    reveal_effect=solari_3
)
carryall = Card(
    name="Carryall",
    persuasion_cost=5,
    icons={Icon.ECONOMY},
    agent_effect=carryall_agent,
    reveal_effect=lambda player: (persuasion_1(player), spice_1(player)),
)
bene_gesserit_sister = Card(
    name="Bene Gesserit Sister",
    persuasion_cost=3,
    icons={Icon.STATECRAFT, Icon.BENE_GESSERIT},
    factions={Faction.BENE_GESSERIT},
    reveal_effect=bene_gesserit_sister_reveal
)
bene_gesserit_initiate = Card(
    name="Bene Gesserit Initiate",
    persuasion_cost=3,
    icons={Icon.ECONOMY, Icon.SETTLEMENT, Icon.STATECRAFT},
    factions={Faction.BENE_GESSERIT},
    agent_effect=draw_card_1,
    reveal_effect=persuasion_1,
)
arrakis_recruiter = Card(
    name="Arrakis Recruiter",
    persuasion_cost=2,
    icons={Icon.SETTLEMENT},
    agent_effect=garrison_1,
    reveal_effect=lambda player: (persuasion_1(player), force_1(player)),
)
assassination_mission = Card(
    name="Assassination Mission",
    persuasion_cost=1,
    reveal_effect=lambda player: (solari_1(player), force_1(player)),
    removal_effect=solari_4,
)
scout = Card(
    name="Scout",
    persuasion_cost=1,
    icons={Icon.SETTLEMENT, Icon.ECONOMY},
    reveal_effect=lambda player: (persuasion_1(player), force_1(player), retreat_2(player)),
)
the_voice = Card(
    name="The Voice",
    persuasion_cost=2,
    icons={Icon.SETTLEMENT, Icon.ECONOMY},
    factions={Faction.BENE_GESSERIT},
    agent_effect=the_voice_agent,
    reveal_effect=persuasion_2,
)
guild_administrator = Card(
    name="Guild Administrator",
    persuasion_cost=2,
    icons={Icon.SPACING_GUILD, Icon.ECONOMY},
    factions={Faction.SPACING_GUILD},
    agent_effect=remove_card,
    reveal_effect=persuasion_1,
)
gun_thopter = Card(
    name="Gun Thopter",
    persuasion_cost=4,
    icons={Icon.SETTLEMENT, Icon.ECONOMY},
    agent_effect=gun_thopter_agent,
    reveal_effect=lambda player: (force_3(player), deploy_1(player)),
)

cards = [firm_grip,
         missionaria_protectiva,
         spice_smugglers,
         gurney_halleck,
         liet_kynes,
         sardaukar_infantry,
         sietch_reverend_mother,
         imperial_spy,
         power_play,
         sardaukar_legion,
         other_memory,
         shifting_allegiances,
         duncan_idaho,
         piter_de_vries,
         worm_riders,
         space_travel,
         thufir_hawat,
         lady_jessica,
         smugglers_thopter,
         test_of_humanity_agent,
         stilgar,
         guild_bankers,
         spice_hunter,
         fedaykin_death_commando,
         opulence,
         kwisatz_haderach,
         guild_ambassador,
         gene_manipulation,
         dr_yueh,
         fremen_camp,
         chani,
         crysknife,
         choam_directorship,
         carryall,
         bene_gesserit_sister,
         bene_gesserit_initiate,
         arrakis_recruiter,
         assassination_mission,
         scout,
         the_voice,
         guild_administrator,
         gun_thopter,
         ]


class ConflictCard:
    def __init__(self, name: str, tier: int, rewards: List[Callable[['Player'], Any]]):
        self.name = name
        self.tier = tier
        self.rewards = rewards


class ConflictCardWithCapture(ConflictCard):
    def __init__(self, name: str, tier: int, rewards: List[Callable[['Player'], Any]],
                 capture_location: CaptureLocation):
        super().__init__(name, tier, rewards)
        self.capture_location = capture_location

    def __repr__(self):
        return f"{self.name} (Tier {self.tier})\t\t{self.rewards}"


no_conflict = ConflictCard(
    name="No Conflict",
    tier=0,
    rewards=[no_effect, no_effect, no_effect]
)

conflict_cards = [
    ConflictCard(
        name='Skirmish I',
        tier=1,
        rewards=[
            victory_point_1,
            water_1,
            spice_1,
        ]
    ),
    ConflictCard(
        name='Skirmish II',
        tier=1,
        rewards=[
            victory_point_1,
            lambda player: (draw_intrigue(player), solari_1(player)),
            solari_2
        ]
    ),
    ConflictCard(
        name='Skirmish III',
        tier=1,
        rewards=[
            lambda player: (choose_influence_1(player), solari_2(player)),
            solari_3,
            solari_2,
        ]
    ),
    ConflictCard(
        name='Skirmish IV',
        tier=1,
        rewards=[
            lambda player: (choose_influence_1(player), solari_1(player)),
            spice_2,
            spice_1,
        ]
    ),
    ConflictCard(
        name='Desert Power',
        tier=2,
        rewards=[
            lambda player: (victory_point_1(player), water_1(player)),
            lambda player: (water_1(player), spice_1(player)),
            spice_1,
        ]
    ),
    ConflictCard(
        name='Cloak and Dagger',
        tier=2,
        rewards=[
            lambda player: (choose_influence_1(player), draw_intrigue(player), draw_intrigue(player)),
            lambda player: (draw_intrigue(player), spice_1(player)),
            cloak_and_dager_3rd,
        ]
    ),
    ConflictCard(
        name='Guild Bank Raid',
        tier=2,
        rewards=[
            solari_6,
            solari_4,
            solari_2,
        ]
    ),
    ConflictCard(
        name='Machinations',
        tier=2,
        rewards=[
            machinations_1st,
            lambda player: (water_1(player), solari_2(player)),
            water_1,
        ]
    ),
    ConflictCard(
        name='Raid Stockpiles',
        tier=2,
        rewards=[
            lambda player: (draw_intrigue(player), spice_3(player)),
            spice_2,
            spice_1,
        ]
    ),
    ConflictCard(
        name='Terrible Purpose',
        tier=2,
        rewards=[
            lambda player: (victory_point_1(player), remove_card(player)),
            lambda player: (water_1(player), spice_1(player)),
            spice_1,
        ]
    ),
    ConflictCard(
        name='Sort Through The Chaos',
        tier=2,
        rewards=[
            lambda player: (get_mentat(player), draw_intrigue(player), solari_2(player)),
            lambda player: (draw_intrigue(player), solari_2(player)),
            solari_2,
        ]
    ),
    ConflictCardWithCapture(
        name='Secure Imperial Basin',
        tier=2,
        capture_location=imperial_basin,
        rewards=[
            victory_point_1,
            water_2,
            water_1,
        ]
    ),
    ConflictCardWithCapture(
        name='Siege of Arrakeen',
        tier=2,
        capture_location=arrakeen,
        rewards=[
            victory_point_1,
            solari_4,
            solari_2,
        ]
    ),
    ConflictCardWithCapture(
        name='Siege of Carthag',
        tier=2,
        capture_location=carthag,
        rewards=[
            victory_point_1,
            lambda player: (draw_intrigue(player), spice_1(player)),
            spice_1,
        ]
    ),
    ConflictCard(
        name='Grand Vision',
        tier=3,
        rewards=[
            lambda player: (choose_influence_2(player), draw_intrigue(player)),
            lambda player: (draw_intrigue(player), spice_3(player)),
            spice_3,
        ]
    ),
    ConflictCardWithCapture(
        name='Battle For Carthag',
        tier=3,
        capture_location=carthag,
        rewards=[
            victory_point_2,
            lambda player: (draw_intrigue(player), spice_3(player)),
            spice_3,
        ]
    ),
    ConflictCardWithCapture(
        name='Battle For Imperial Basin',
        tier=3,
        capture_location=imperial_basin,
        rewards=[
            victory_point_2,
            spice_5,
            spice_3,
        ]
    ),
    ConflictCardWithCapture(
        name='Battle For Arrakeen',
        tier=3,
        capture_location=arrakeen,
        rewards=[
            victory_point_2,
            battle_for_arrakeen_2nd,
            lambda player: (draw_intrigue(player), solari_2(player)),
        ]
    ),
]


class Intrigue:
    def __init__(self, name: str, effect: Callable[['Player'], Any],
                 intrigue_types=None, copies: int = 10):
        if intrigue_types is None:
            intrigue_types = {IntrigueType.PLOT}
        self.name: str = name
        self.effect: Callable[['Player'], Any] = effect
        self.intrigue_types: Set[IntrigueType] = intrigue_types
        self.copies = copies

    def get_instances(self):
        return [
            IntrigueInstance(i, self.name, self.effect, self.intrigue_types)
            for i in range(self.copies)
        ]

    def __repr__(self):
        return self.name


class IntrigueInstance:
    def __init__(self, id: int, name: str, effect: Callable[['Player'], Any], intrigue_types: Set[IntrigueType]):
        self.name: str = name
        self.effect: Callable[['Player'], Any] = effect
        self.intrigue_types: Set[IntrigueType] = intrigue_types
        self.id = id

    def __repr__(self):
        return self.name


no_intrigue = Intrigue("no Intrigue", no_effect)

plots = [
    Intrigue(
        name="Dispatch an Envoy ",
        effect=dispatch_an_envoy
    ),
    Intrigue(
        name='Secrets Of The Sisterhood',
        effect=influence_bene_gesserit_1,
    ),
    Intrigue(
        name='Favored Subjects',
        effect=influence_emperor_1,
    ),
    Intrigue(
        name='Know Their Ways',
        effect=influence_fremen_1,
    ),
    Intrigue(
        name='Guild Authorization',
        effect=influence_spacing_guild_1,
    ),
    Intrigue(
        name='Windfall',
        effect=solari_2,
    ),
    Intrigue(
        name='Water Peddlers Union',
        effect=water_1,
    ),
    Intrigue(
        name='Charisma',
        effect=persuasion_2,
    ),
    Intrigue(
        name='Rapid Mobilization',
        effect=deploy_all,
    ),
    Intrigue(
        name='Reinforcements',
        effect=reinforcements,
    ),
    Intrigue(
        name='The Sleeper Must Awaken',
        effect=the_sleeper_must_awaken,
    ),
    Intrigue(
        name='Choam Shares',
        effect=choam_shares,
    ),
    Intrigue(
        name='Refocus',
        effect=refocus,
    ),
    Intrigue(
        name='Bribery',
        effect=bribery,
    ),
    Intrigue(
        name='Double Cross',
        effect=double_cross,
    ),
    Intrigue(
        name='Infiltrate',
        effect=infiltrate,
    ),
    Intrigue(
        name='Councilor\'s Dispensation',
        effect=councilors_dispensation,
    ),
    Intrigue(
        name='Double Cross',
        effect=double_cross,
    ),
    Intrigue(
        name='Water of Life',
        effect=water_of_life,
    ),
    Intrigue(
        name='Poisons Snooper',
        effect=poisons_snooper,
    ),
    Intrigue(
        name='Double Cross',
        effect=double_cross,
    ),
    Intrigue(
        name='Urgent  Mission',
        effect=double_cross,
    ),
    Intrigue(
        name='Recruitment  Mission',
        effect=recruitment_mission,
    ),
    Intrigue(
        name='Bindu Suspension',
        effect=bindu_suspension,
    ),
    Intrigue(
        name='Calculated Hire',
        effect=recruitment_mission,
    ),
    Intrigue(
        name='Bypass Protocol',
        effect=bypass_protocol,
    ),
    # Combat

    Intrigue(
        name='Ambush',
        intrigue_types={IntrigueType.COMBAT},
        effect=force_4
    ),
    Intrigue(
        name='Ambush',
        intrigue_types={IntrigueType.COMBAT},
        effect=staged_incident
    ),
    Intrigue(
        name='Private Army',
        intrigue_types={IntrigueType.COMBAT},
        effect=private_army
    ),
    Intrigue(
        name='Allied Armada',
        intrigue_types={IntrigueType.COMBAT},
        effect=allied_armada
    ),
    Intrigue(
        name='Demand Respect',
        intrigue_types={IntrigueType.COMBAT},
        effect=demand_respect
    ),
    Intrigue(
        name='To the Victor...',
        intrigue_types={IntrigueType.COMBAT},
        effect=to_the_victor
    ),
    Intrigue(
        name='Tiebreaker',
        intrigue_types={IntrigueType.COMBAT, IntrigueType.FINALE},
        effect=tiebreaker
    ),
    Intrigue(
        name='Corner the Market',
        intrigue_types={IntrigueType.FINALE},
        effect=to_the_victor
    ),

    # Finale
    Intrigue(
        name='Corner the Market',
        intrigue_types={IntrigueType.FINALE},
        effect=corner_the_market
    ),
    Intrigue(
        name='Plans Within Plans',
        intrigue_types={IntrigueType.FINALE},
        effect=plans_within_plans
    ),

]
