from typing import List
from transitions import Machine

import demo_cards as dc
import demo_board as db
import demo_player as dp

class Game:
    def __init__(self, player_count: int = 4):
        self.cards: List[dc.Card] = dc.cards
        self.plots: List[dc.PlotIntrigue] = dc.plots
        self.shop: List[dc.Card] = self.cards[1:]
        self.locations: List[db.Location] = db.locations
        self.players: List[dp.Player] = [dp.Player(self) for _ in range(player_count)]
        self.current_player: dp.Player = self.players[0]

    def set_game_machine(self, machine: Machine):
        self.game_machine: Machine = machine

    def get_legal_triggers(self):
        triggers = self.game_machine.get_triggers(self.state)
        triggers = list(filter(lambda trigger: not trigger.startswith('to_'), triggers))
        legal_triggers = []
        for trigger in triggers:
            if getattr(self, f'may_{trigger}')():
                legal_triggers.append(trigger)
        return list(set(legal_triggers))

    def walk(self):
        while True:
            current_state = self.game_machine.get_state(self.state).name
            print(f'Current State: {current_state} [$ {self.current_player.money}, S {self.current_player.spice}]')
            # if self.state == 'agent_turn':
            #     self.trigger('back')
            triggers = self.get_legal_triggers()
            if len(triggers) == 0:
                raise Exception("Dead End state!")
            print('Actions:')
            [print(f'\t{i} - {trigger}') for i, trigger in enumerate(triggers)]
            self.update_graph_picture()
            choice = int(input(f"Choose an Action (0-{len(triggers)-1}): "))
            self.trigger(triggers[choice])

    def update_graph_picture(self):
        import re
        import graphviz
        replacements = [
            ('play_', 'play_card_to_location'),
            ('plot_', 'plot_card'),
            ('buy_', 'buy_card'),
            ('deploy_', 'deploy_troops'),
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
                pretty_graph += re.sub(r'"[^"]*"', '"' + '\n'.join(occurring) + '"', graph_line) + '\n'
            else:
                pretty_graph += graph_line + '\n'




        modified_graph = graphviz.Source(pretty_graph)
        modified_graph.render('resources/state_diagram', format='png')