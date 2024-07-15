from Choice import *
from enums import Statics, CardName, LocationName, Icon


def no_effect(player: 'Player'):
    pass


def persuasion_1(player: 'Player'):
    player.change_persuasion(1)


def persuasion_2(player: 'Player'):
    player.change_persuasion(2)


def persuasion_3(player: 'Player'):
    player.change_persuasion(3)


def persuasion_4(player: 'Player'):
    player.change_persuasion(4)


def spice_1(player: 'Player'):
    player.change_spice(1)


def spice_2(player: 'Player'):
    player.change_spice(2)


def spice_3(player: 'Player'):
    player.change_spice(3)


def spice_5(player: 'Player'):
    player.change_spice(5)


def solari_1(player: 'Player'):
    player.change_solari(1)


def solari_2(player: 'Player'):
    player.change_solari(2)


def solari_3(player: 'Player'):
    player.change_solari(3)


def solari_4(player: 'Player'):
    player.change_solari(4)


def solari_5(player: 'Player'):
    player.change_solari(5)


def solari_6(player: 'Player'):
    player.change_solari(6)


def water_1(player: 'Player'):
    player.change_water(1)


def water_2(player: 'Player'):
    player.change_water(2)


def victory_point_1(player: 'Player'):
    player.change_victory_points(1)


def victory_point_2(player: 'Player'):
    player.change_victory_points(2)


def draw_card_1(player: 'Player'):
    player.draw(1)


def draw_card_2(player: 'Player'):
    player.draw(2)


def draw_card_3(player: 'Player'):
    player.draw(3)


def draw_intrigue(player: 'Player'):
    player.draw_intrigue()


def remove_card(player: 'Player'):
    card = removable_cards_choice.resolve(player)
    player.remove_card(card)


# should only be used to get mentat for next round
def get_mentat(player: 'Player'):
    player.add_mentat()


def force_1(player: 'Player'):
    player.change_force(1)


def force_2(player: 'Player'):
    player.change_force(2)


def force_3(player: 'Player'):
    player.change_force(3)


def force_4(player: 'Player'):
    player.change_force(4)


def force_5(player: 'Player'):
    player.change_force(5)


def force_6(player: 'Player'):
    player.change_force(6)


def garrison_1(player: 'Player'):
    player.change_garrison(1)


def garrison_2(player: 'Player'):
    player.change_garrison(2)


def garrison_4(player: 'Player'):
    player.change_garrison(4)


def garrison_5(player: 'Player'):
    player.change_garrison(5)


def deploy_1(player: 'Player'):
    player.change_to_deploy(1)


def deploy_2(player: 'Player'):
    player.change_to_deploy(2)


def deploy_all(player: 'Player'):
    player.change_to_deploy(Statics.MAX_TROOPS)


def enter_combat(player: 'Player'):
    player.agent_on_combat_location = True
    deploy_2(player)


def retreat_all(player: 'Player'):
    player.change_to_retreat(Statics.MAX_TROOPS)


def retreat_2(player: 'Player'):
    player.change_to_retreat(2)


def influence_fremen_1(player: 'Player'):
    player.change_influence(Faction.FREMEN, 1)


def influence_emperor_1(player: 'Player'):
    player.change_influence(Faction.EMPEROR, 1)


def influence_spacing_guild_1(player: 'Player'):
    player.change_influence(Faction.SPACING_GUILD, 1)


def influence_bene_gesserit_1(player: 'Player'):
    player.change_influence(Faction.BENE_GESSERIT, 1)


def choose_influence_1(player: 'Player'):
    faction = influence_choice(1, set()).resolve(player)
    player.change_influence(faction, 1)


def choose_influence_2(player: 'Player'):
    faction = influence_choice(2, set()).resolve(player)
    player.change_influence(faction, 2)


# a bit hacky, but removes card with this name from the played cards, i.e. self deletion. Names should be at least managed with an enum
def self_remove(player: 'Player', card_name: CardName):
    card = player.played_cards.find(lambda card: card.name == card_name.name)
    player.remove_card(card)


def seek_allies_agent(player: 'Player'):
    self_remove(player, CardName.SEEK_ALLIES)


def firm_grip_agent(player: 'Player'):
    if player.solari >= 2:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_solari(-2)
            faction = influence_choice(1, {Faction.EMPEROR}).resolve(player)
            player.change_influence(faction, 1)


def firm_grip_reveal(player: 'Player'):
    if Faction.EMPEROR in player.alliances:
        player.change_persuasion(4)


def missionaria_protectiva_agent(player: 'Player'):
    if player.get_in_play(Faction.BENE_GESSERIT) >= 2:
        choose_influence_1(player)


def spice_smugglers_agent(player: 'Player'):
    if player.spice >= 2:
        player.change_spice(-2)
        player.change_influence(Faction.SPACING_GUILD, 1)
        player.change_solari(3)


def gurney_halleck_reveal(player: 'Player'):
    player.change_persuasion(2)
    if player.solari >= 3:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_solari(-3)
            player.change_garrison(2)
            player.change_to_deploy(2)


def liet_kynes_reveal(player: 'Player'):
    in_play = player.get_in_play(Faction.FREMEN)
    player.change_persuasion(in_play)


def sietch_reverend_mother_reveal(player: 'Player'):
    if player.get_in_potential_play(Faction.BENE_GESSERIT) >= 2:
        player.change_persuasion(3)
        player.change_garrison(2)


def imerial_spy_agent(player: 'Player'):
    choice = bool_choice.resolve(player)
    if choice:
        self_remove(player, CardName.IMPERIAL_SPY)
        player.draw_intrigue()


def power_play_agent(player: 'Player'):
    if player.current_location.faction in Faction:
        player.change_influence(player.current_location.faction, 1)
        self_remove(player, CardName.POWER_PLAY)


def other_memory_agent(player: 'Player'):
    if player.get_in_discard(Faction.BENE_GESSERIT):
        choice = bool_choice.resolve(player)
        if choice:
            card_choice = discard_pile_bene_gesserit_choice.resolve(player)
            player.draw_from_discard(card_choice)
        else:
            player.draw(1)


def shifting_allegiances_agent(player: 'Player'):
    if player.get_changeable_factions(-1) and player.spice >= 2:
        choice = bool_choice.resolve(player)
        if choice:
            donor_faction = influence_choice(-1, set()).resolve(player)
            receiver_faction = influence_choice(2, set()).resolve(player)
            player.change_influence(donor_faction, -1)
            player.change_influence(receiver_faction, 2)
            player.change_spice(-2)


def duncan_idaho_agent(player: 'Player'):
    if player.water >= 1:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_water(-1)
            player.change_garrison(1)
            player.draw(1)


def worm_riders_reveal(player: 'Player'):
    if player.factions[Faction.FREMEN]['influence'] >= 2:
        player.change_force(4)
        if Faction.FREMEN in player.alliances:
            player.change_force(2)


def smugglers_thopter_agent(player: 'Player'):
    if player.factions[Faction.SPACING_GUILD]['influence'] >= 2:
        player.draw(2)


# ToDo: edge cases (no cards and in_combat)
def test_of_humanity_agent(player: 'Player'):
    for other_player in player.game.players:
        if other_player is player:
            continue
        if other_player.in_combat:
            choice = bool_choice.resolve(other_player)
            if choice:
                player.change_in_combat(-1)
                return
        card_choice = hand_card_choice.resolve(other_player)
        player.discard(card_choice)


def guild_bankers_reveal(player: 'Player'):
    player.guild_bankers = True


def spice_hunter_reveal(player: 'Player'):
    player.change_persuasion(1)
    player.change_force(1)
    if player.get_in_potential_play(Faction.FREMEN) >= 2:
        player.change_spice(1)


def fedaykin_death_commando_reveal(player: 'Player'):
    player.change_force(1)
    if player.get_in_potential_play(Faction.FREMEN) >= 2:
        player.change_force(3)


def opulence_reveal(player: 'Player'):
    player.change_persuasion(1)
    if player.solari >= 6:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_solari(-6)
            player.change_victory_points(1)


def kwisatz_haderach_agent(player: 'Player'):
    player.draw(1)
    agent_choice = kwisatz_location_choice.resolve(player)
    destination_choice = kwisatz_destination_choice.resolve(player)
    player.current_location = destination_choice
    if agent_choice.name is LocationName.AGENT_RESERVES.value:
        player.agents -= 1
    else:
        agent_choice.occupied_by.remove(player)
    destination_choice.occupy(player)
    destination_choice.requirement.fulfill(player)
    destination_choice.effect(player)


def guild_ambassador_agent(player: 'Player'):
    choice = bool_choice.resolve(player)
    if choice:
        player.change_influence(Faction.SPACING_GUILD, 1)
    else:
        player.change_spice(2)


def guild_ambassador_reveal(player: 'Player'):
    if Faction.SPACING_GUILD in player.alliances:
        if player.spice >= 3:
            choice = bool_choice.resolve(player)
            if choice:
                player.change_spice(-3)
                player.change_victory_points(1)


def gene_manipulation_agent(player: 'Player'):
    remove_card(player)
    if player.get_in_play(Faction.BENE_GESSERIT) >= 2:
        player.change_spice(2)


def fremen_camp_agent(player: 'Player'):
    if player.spice >= 2:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-2)
            player.change_garrison(3)


def crysknife_reveal(player: 'Player'):
    player.change_force(1)
    if player.get_in_potential_play(Faction.FREMEN) >= 2:
        player.change_influence(Faction.FREMEN, 1)


def carryall_agent(player: 'Player'):
    if player.current_location.name is LocationName.IMPERIAL_BASIN.value:
        player.change_spice(1)
    elif player.current_location.name is LocationName.HAGGA_BASIN.value:
        player.change_garrison(2)
    elif player.current_location.name is LocationName.THE_GREAT_FLAT.value:
        player.change_spice(3)


def bene_gesserit_sister_reveal(player: 'Player'):
    choice = bool_choice.resolve(player)
    if choice:
        player.change_persuasion(2)
    else:
        player.change_force(2)


def the_voice_agent(player: 'Player'):
    location_choice = voice_location_choice.resolve(player)
    location_choice.voiced = True
    for other_player in player.game.players:
        if other_player is player:
            continue
        other_player.voice = True


def gun_thopter_agent(player: 'Player'):
    for other_player in player.game.players:
        if other_player is player:
            continue
        other_player.change_garrison(-1)


# Conflict
def cloak_and_dager_3rd(player: 'Player'):
    choice = bool_choice.resolve(player)
    if choice:
        player.draw_intrigue()
    else:
        player.change_spice(1)


def machinations_1st(player: 'Player'):
    faction_choice_1 = influence_choice(1, set()).resolve(player)
    player.change_influence(faction_choice_1, 1)
    faction_choice_2 = influence_choice(1, {faction_choice_1}).resolve(player)
    player.change_influence(faction_choice_2, 1)


def battle_for_arrakeen_2nd(player: 'Player'):
    # workaround for "choose 2 of 3"
    choice_1 = bool_choice.resolve(player)
    if choice_1:
        player.draw_intrigue()
        choice_2 = bool_choice.resolve(player)
        if choice_2:
            player.change_spice(2)
        else:
            player.change_solari(3)
    else:
        player.change_spice(2)
        choice_2 = bool_choice.resolve(player)
        if choice_2:
            player.draw_intrigue()
        else:
            player.change_solari(3)


# Intrigues
def dispatch_an_envoy(player: 'Player'):
    player.add_icons({Icon.EMPEROR, Icon.SPACING_GUILD, Icon.BENE_GESSERIT, Icon.FREMEN})


def reinforcements(player: 'Player'):
    if player.solari >= 3:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_garrison(3)
            player.change_solari(-2)
            if player.is_revealing_turn:
                player.change_to_deploy(3)


def the_sleeper_must_awaken(player: 'Player'):
    if player.spice >= 4:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-4)
            player.change_victory_points(1)


def choam_shares(player: 'Player'):
    if player.solari >= 7:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_solari(-7)
            player.change_victory_points(1)


def refocus(player: 'Player'):
    player.deck.extend(player.discard_pile)
    random.shuffle(player.discard_pile)
    player.discard_pile.clear()
    player.draw(1)


def bribery(player: 'Player'):
    if player.spice >= 2:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-2)
            choose_influence_1(player)


def double_cross(player: 'Player'):
    if player.solari >= 1:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_solari(-1)
            player_choice = other_players_choice.resolve(player)
            player_choice.change_in_combat(-1)
            player.change_to_deploy(1)


def infiltrate(player: 'Player'):
    player.infiltrate = True


def councilors_dispensation(player: 'Player'):
    if player.is_in_high_council():
        player.change_spice(2)


def water_of_life(player: 'Player'):
    if player.water >= 1 and player.spice >= 1:
        choice = bool_choice.resolve(player)
        if choice:
            player.draw(3)


# ToDo: how to add information to model? Maybe Paul slot?
def poisons_snooper(player: 'Player'):
    # ToDo: add information to input model
    choice = bool_choice.resolve(player)
    if choice:
        player.draw(1)
    else:
        player.remove_deck_top()


def urgent_mission(player: 'Player'):
    # check if player has used any agents
    agent_choice = urgent_mission_location_choice.resolve(player)
    agent_choice.occupied_by.remove(player)
    player += 1


def recruitment_mission(player: 'Player'):
    player.change_persuasion(1)
    player.recruitment = True


def bindu_suspension(player: 'Player'):
    if not player.in_turn:
        player.draw(1)
        player.bindu_suspension = True


def calculated_hire(player: 'Player'):
    if player.spice >= 1 and player.game.mentat_available:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-1)
            player.try_add_mentat()


def bypass_protocol(player: 'Player'):
    cheap = bool_choice.resolve(player)
    if cheap:
        card_choice = bypass_protocol_3_choice.resolve(player)
        player.game.shop.get_card(card_choice, player)
    else:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-2)
            card_choice = bypass_protocol_5_choice.resolve(player)
            player.game.shop.get_card(card_choice, player)


def staged_incident(player: 'Player'):
    if player.in_combat >= 3:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_in_combat(-3)
            player.change_victory_points(1)


def private_army(player: 'Player'):
    if player.spice >= 2:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-2)
            player.change_force(5)


def allied_armada(player: 'Player'):
    if player.spice >= 2 and player.alliances:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-2)
            player.change_force(7)


def master_tactician(player: 'Player'):
    choice = bool_choice.resolve(player)
    if choice:
        player.change_force(3)
    else:
        player.change_to_retreat(3)


def demand_respect(player: 'Player'):
    player.on_win.append(_demand_respect)


def _demand_respect(player: 'Player'):
    if player.spice >= 2:
        choice = bool_choice.resolve(player)
        if choice:
            player.change_spice(-2)
            choose_influence_2(player)
        else:
            choose_influence_1(player)


def _to_the_victor(player: 'Player'):
    player.change_spice(3)


def to_the_victor(player: 'Player'):
    player.on_win.append(_to_the_victor)


def tiebreaker(player: 'Player'):
    if player.in_finale:
        player.change_spice(10)
    else:
        player.change_force(2)


def _count_tsmf(player: 'Player'):
    all_player_cards = player.get_all_cards()
    return all_player_cards.count(lambda card: card.name == CardName.THE_SPICE_MUST_FLOW.value)

def corner_the_market(player: 'Player'):
    player_tsmf = _count_tsmf(player)

    if player_tsmf >= 2:
        player.change_victory_points(1)

    max_tsmf = max([_count_tsmf(other_player) for other_player in player.game.players if
                     other_player is not player])

    if player_tsmf > max_tsmf:
        player.change_victory_points(1)


def plans_within_plans(player: 'Player'):
    more_than_3 = len([faction for faction in player.factions.keys() if player.factions[faction]['influence'] >= 3])
    if more_than_3 >= 4:
        player.change_victory_points(2)
    elif more_than_3 >= 3:
        player.change_victory_points(1)


def sell_melange(player):
    spice_amount = spice_trade_choice.resolve(player)
    # we already paid 2 spice upfront, before evaluation to ensure that we
    # can go to this field
    player.change_spice(-2 - spice_amount)
    player.change_solari(6 + (2 * (spice_amount - 2)))


def swordmaster(player):
    player.add_swordmaster(player)


def mentat(player):
    player.try_add_mentat()
    player.draw(1)


def high_council(player):
    player.enter_high_council()


def fold_space(player):
    player.draw_foldspace()


def steal_intrigue(player):
    for other_player in player.game.players:
        if other_player is player:
            continue
        if len(player.intrigues) > 3:
            random.shuffle(other_player.intrigues)
            player.intrigues.append(other_player.intrigues.pop())
