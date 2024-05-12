from typing import List
from transitions import Machine
from logger import Logger


import demo_cards as dc
import demo_board as db
import demo_player as dp
from enums import Commander

import time
import random


class Game:
    def __init__(self, player_count: int = 4):
        random.seed(123)

        self.cards: List[dc.Card] = dc.cards
        self.plots: List[dc.PlotIntrigue] = dc.plots
        self.shop: List[dc.Card] = []  # self.cards[1:]
        self.locations: List[db.Location] = db.locations
        self.num_players = player_count
        self.players: List[dp.Player] = [dp.Player(self, commander_name) for commander_name in random.sample(list(Commander), player_count)]
        self.current_player: dp.Player = self.players[0]
        self.max_troops = 12
        self.max_influence = 6

        self.logger = Logger(self)

    def set_game_machine(self, machine: Machine):
        self.game_machine: Machine = machine


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


    def walk(self):
        while True:
            actions = self.get_legal_actions()
            if len(actions) == 0:
                raise Exception("Dead End state!")

            self.print_game_state(actions)
            self.update_graph_picture()

            choice = int(input(f"Choose an Action (0-{len(actions) - 1}): "))
            print(f"CHOICE: {actions[choice]} ({choice})\n")
            self.trigger(actions[choice])
            print("\n----------------------------------------------------------------------------------")


    def auto_walk(self):
        while True:
            start = time.time()
            actions = self.get_legal_actions()

            choice = random.randint(0, len(actions) - 1)
            self.logger.print_game_state(actions, choice)
            if len(actions) == 0:
                raise Exception("Dead End state!")

            self.trigger(actions[choice])

            self.logger.print_changes()

            for player in self.players:
                player.str_out = ""
            stop = time.time()
            # print(f"Turn Time: {stop - start}")


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





