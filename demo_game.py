from typing import List
from transitions import Machine
from logger import Logger
from itertools import groupby

import demo_board as db
import demo_player as dp
from demo_cards import conflict_cards
from enums import Commander, GameState
from Shop import Shop
import time
import random


class Game:
    def __init__(self, player_count: int = 4):
        random.seed(123)

        self.locations: List[db.Location] = db.locations
        self.num_players = player_count
        self.max_troops = 12
        self.max_influence = 6
        self.logger = Logger(self)
        self.shop = Shop(self)
        self.players: List[dp.Player] = [dp.Player(self, commander_name) for commander_name in random.sample(list(Commander), player_count)]
        self.current_player: dp.Player = self.players[0]
        self.game_state: GameState = GameState.AGENT
        self.conflict_cards: List['ConflictCard'] = conflict_cards
        self.mentat_available = True
        random.shuffle(self.conflict_cards)
        self.worm_locations = {location: 0 for location in self.locations if
                                location.name in ['Imperial Basin', 'Hagga Basin', 'The Great Flat']}
        self.capture_locations = {location: None for location in self.locations if
                                location.name in ['Imperial Basin', 'Arrakeen', 'Carthag']}
        self.current_conflict: 'ConflictCard' = None
        self.choose_next_conflict()
        self.round_number = 0

    def get_current_conflict(self):
        return self.current_conflict
    def choose_next_conflict(self):
        # return self.conflict_cards[-1]
        self.current_conflict = random.sample(self.conflict_cards, 1)[0]


    def get_location(self, location_name):
        return next(location for location in self.locations if location.name == location_name)

    def check_game_state(self):
        all_revealed = True
        none_intrigue = True
        all_resolved = True
        for player in self.players:
            if not player.has_revealed():
                all_revealed = False
            if player.has_played_intrigue:
                none_intrigue = False
            if not player.has_resolved_conflict:
                all_resolved = False

        if all_revealed:
            self.game_state = GameState.IN_CONFLICT

        if self.game_state == GameState.IN_CONFLICT and none_intrigue:
            self.resolve_combat()
            self.game_state = GameState.CONFLICT_OVER

        if self.game_state == GameState.CONFLICT_OVER and all_resolved:
            self.game_state = GameState.AGENT
            # removed this for debugigng
            # self.conflict_cards.pop()
            # Let the Worm Poop
            for worm_location in self.worm_locations.keys():
                if not worm_location.is_occupied:
                    self.worm_locations[worm_location] += 1
            for location in self.locations:
                location.is_occupied = False
            self.mentat_available = True
            for player in self.players:
                player.has_resolved_conflict = False
            self.choose_next_conflict()

            self.round_number += 1

    def mentat_is_available(self):
        return self.mentat_available
    def resolve_combat(self):
        forces = {}
        for player in self.players:
            actual_force = player.force if player.in_combat > 0 else 0
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
                # print(f'{player} placed {placement}')
                player.set_conflict_ranking(placement)
            current_placement += len(equal_players)



    def set_game_machine(self, machine: Machine):
        self.game_machine: Machine = machine

    def is_in_battle_state(self):
        return self.game_state == GameState.BATTLE
    def advance_player(self):
        self.current_player = self.players[(self.players.index(self.current_player) + 1) % self.num_players]

    def get_legal_actions(self):
        triggers = self.game_machine.get_triggers(self.state)
        triggers = list(filter(lambda trigger: not trigger.startswith('to_'), triggers))
        legal_triggers = []
        for trigger in triggers:
            if getattr(self, f'may_{trigger}')():
                legal_triggers.append(trigger)
        legal_triggers.sort()
        return list(legal_triggers)


    def walk(self, debug=False, move_list=[], auto=False):
        skipable_actions = {
            'done_reveal',
            'decide_card',
            'evaluate_choices_reveal',
            'evaluate_choices_plot',
            'evaluate_choices_agent_location',
            'get_conflict_reward',
            'evaluate_choices_conflict',
            'swap_player',
        }

        while True:
            start = time.time()
            actions = self.get_legal_actions()

            if len(actions) == 1 and actions[0] in skipable_actions and not debug:
                # random to not change seed behaviour between debug and non-debug
                self.trigger(actions[random.randint(0, 0)])
                continue

            self.logger.print_game_state(actions)
            choice = self.logger.choose_action(actions, move_list, auto)
            self.logger.print_changes()

            self.sanity_check(actions, skipable_actions)
            self.trigger(actions[choice])

            stop = time.time()
            # print(f"Turn Time: {stop - start}")



    def sanity_check(self, actions, skipable_actions):
        if len(actions) == 0:
            raise Exception("Dead End state!")
        if len(set(actions).intersection(skipable_actions)) > 0 and len(actions) > 1:
            raise Exception("Skipable actions should be the only actions available")

    def update_graph_picture(self):
        import re
        import graphviz
        replacements = [
            ('choice_', '<CHOICE>'),
            ('card_', '<CARD>'),
            ('plot_', '<PLOT_INTRIGUE>'),
            ('location_', '<LOCATION>'),
            ('buy_', 'buy_<CARD>'),
            ('deploy_', 'deploy_<N>_troops'),
        ]
        graph = self.game_machine.get_graph(show_roi=False)
        graph_string = str(graph)
        pretty_graph = ""
        for graph_line in graph_string.split('\n'):
            occurring = []
            for old, new in replacements:
                if old in graph_line:
                    occurring.append(new)
            if len(occurring) != 0:
                pretty_graph += graph_line.split('[')[0] + f"[label=\"{' | '.join(occurring)}\"]\n"
            else:
                pretty_graph += graph_line + '\n'
        pretty_graph = pretty_graph.replace('}', '\trankdir=TB\n}')
        modified_graph = graphviz.Source(pretty_graph)
        modified_graph.render('resources/state_diagram', format='png')





