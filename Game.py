from typing import List
import random

from Location import locations, SpiceCollectingLocation, Location
from Cards import conflict_cards, no_conflict, ConflictCardWithCapture, ConflictCard
from Shop import Shop
from Player import Player
from enums import Commander, GameState, Statics


class Game:
    def __init__(self, player_count: int = 4):
        random.seed(123)

        self.locations: List['Location'] = locations
        self.num_players = player_count
        # ToDo: make this stuff static
        self.shop = Shop()
        self.players: List[Player] = [Player(self, commander_name) for commander_name in
                                      random.sample(list(Commander), player_count)]
        self.current_player: Player = self.players[0]
        self.game_state: GameState = GameState.AGENT
        self.conflict_cards: List['ConflictCard'] = conflict_cards
        self.mentat_available = True
        random.shuffle(self.conflict_cards)
        self.current_conflict: 'ConflictCard' = no_conflict

        self.round_number = 0

    def all_revealed(self):
        for player in self.players:
            if not player.has_revealed():
                return False
        return True

    def all_passed(self):
        for player in self.players:
            if not player.passed_combat_intrigue():
                return False
        return True

    def game_over(self):
        max_rounds = self.round_number > 10
        vp_threshold = any(player.victory_points >= 10 for player in self.players)
        return max_rounds or vp_threshold

    def reset_locations(self):
        for location in self.locations:
            location.clear()

    def add_to_spice_collecting_locations(self):
        for worm_location in filter(lambda loc: isinstance(loc, SpiceCollectingLocation) and not loc.occupied_by,
                                    self.locations):
            worm_location.collected_spice += 1

    def set_new_conflict(self):
        self.current_conflict = self.conflict_cards.pop()
        if isinstance(self.current_conflict, ConflictCardWithCapture):
            player = self.current_conflict.capture_location.captured_by
            # if location is captured player gets a defense bonus of one troop
            if player:
                if player.garrison != Statics.MAX_TROOPS:
                    player.change_in_combat(1)
                else:
                    player.deploy(1)

    def simulate_game(self):
        while not self.game_over():

            self.set_new_conflict()

            while not self.all_revealed():
                for current_player_id in range(self.num_players):
                    current_player = self.players[current_player_id + self.round_number % self.num_players]
                    if not current_player.has_revealed():
                        current_player.agent_or_reveal_turn()

            while not self.all_passed():
                for current_player_id in range(self.num_players):
                    current_player = self.players[current_player_id + self.round_number % self.num_players]
                    current_player.combat_turn()

            self.resolve_combat()
            self.add_to_spice_collecting_locations()
            self.reset_locations()
            self.mentat_available = True

            self.reset_players()

        for current_player_id in range(self.num_players):
            current_player = self.players[current_player_id + self.round_number % self.num_players]
            current_player.finale_turn()

    def reset_players(self):
        for player in self.players:
            player.after_conflict()

    def resolve_combat(self):
        forces = {}
        for player in self.players:
            actual_force = player.force + (player.in_combat * 2) if player.in_combat > 0 else 0
            if actual_force not in forces:
                forces[actual_force] = [player]
            else:
                forces[actual_force].append(player)
        sorted_forces = sorted(forces.keys(), reverse=True)

        current_placement = 0
        for force in sorted_forces:
            equal_players = forces[force]
            placement = len(equal_players) - 1 + current_placement
            for player in equal_players:
                # last place gets no reward + you must have forces to get a reward
                if placement < self.num_players and force > 0:
                    self.current_conflict.rewards[placement](player)
                    if placement == 0:
                        # if there is a first place win combat intrigues get triggered
                        for win_effect in player.on_win:
                            win_effect(player)
                        # if there is a first place in a capture conflict this player gets the location
                        if isinstance(self.current_conflict, ConflictCardWithCapture):
                            self.current_conflict.capture_location.captured_by += player

            current_placement += len(equal_players)

    # def set_game_machine(self, machine: Machine):
    #     self.game_machine: Machine = machine
    #
    # def is_in_battle_state(self):
    #     return self.game_state == GameState.BATTLE
    # def advance_player(self):
    #     self.current_player = self.players[(self.players.index(self.current_player) + 1) % self.num_players]
    #
    # def get_legal_actions(self):
    #     triggers = self.game_machine.get_triggers(self.state)
    #     triggers = list(filter(lambda trigger: not trigger.startswith('to_'), triggers))
    #     legal_triggers = []
    #     for trigger in triggers:
    #         if getattr(self, f'may_{trigger}')():
    #             legal_triggers.append(trigger)
    #     legal_triggers.sort()
    #     return list(legal_triggers)

    # def walk(self, debug=False, move_list=[], auto=False):
    #     skipable_actions = {
    #         'done_reveal',
    #         'decide_card',
    #         'evaluate_choices_reveal',
    #         'evaluate_choices_plot',
    #         'evaluate_choices_agent_location',
    #         'get_conflict_reward',
    #         'evaluate_choices_conflict',
    #         'swap_player',
    #     }
    #
    #     while True:
    #         start = time.time()
    #         actions = self.get_legal_actions()
    #
    #         if len(actions) == 1 and actions[0] in skipable_actions and not debug:
    #             # random to not change seed behaviour between debug and non-debug
    #             self.trigger(actions[random.randint(0, 0)])
    #             continue
    #
    #         self.logger.print_game_state(actions)
    #         choice = self.logger.choose_action(actions, move_list, auto)
    #         self.logger.print_changes()
    #
    #         self.sanity_check(actions, skipable_actions)
    #         self.trigger(actions[choice])
    #
    #         stop = time.time()
    #         # print(f"Turn Time: {stop - start}")

    # def sanity_check(self, actions, skipable_actions):
    #     if len(actions) == 0:
    #         raise Exception("Dead End state!")
    #     if len(set(actions).intersection(skipable_actions)) > 0 and len(actions) > 1:
    #         raise Exception("Skipable actions should be the only actions available")

    # def update_graph_picture(self):
    #     import re
    #     import graphviz
    #     replacements = [
    #         ('choice_', '<CHOICE>'),
    #         ('card_', '<CARD>'),
    #         ('plot_', '<PLOT_INTRIGUE>'),
    #         ('location_', '<LOCATION>'),
    #         ('buy_', 'buy_<CARD>'),
    #         ('deploy_', 'deploy_<N>_troops'),
    #     ]
    #     graph = self.game_machine.get_graph(show_roi=False)
    #     graph_string = str(graph)
    #     pretty_graph = ""
    #     for graph_line in graph_string.split('\n'):
    #         occurring = []
    #         for old, new in replacements:
    #             if old in graph_line:
    #                 occurring.append(new)
    #         if len(occurring) != 0:
    #             pretty_graph += graph_line.split('[')[0] + f"[label=\"{' | '.join(occurring)}\"]\n"
    #         else:
    #             pretty_graph += graph_line + '\n'
    #     pretty_graph = pretty_graph.replace('}', '\trankdir=TB\n}')
    #     modified_graph = graphviz.Source(pretty_graph)
    #     modified_graph.render('resources/state_diagram', format='png')
