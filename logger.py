import random

class Logger:
    def __init__(self, game: 'Game'):
        self.game = game
        self.max_width = 300
        self.cols = 4
        self.col_space = 3
        self.line_size = self.max_width // self.cols
        self.target_len = self.line_size - self.col_space

    def fix_string_length(self, string, target_len):
        return (string + ' ' * (self.max_width - len(string)))[0:target_len] + '|'

    def print_linebreak(self, strings):
        num_strings = len(strings)
        overflow = {player: '' for player in range(num_strings)}
        has_overflow = False
        for player, string in enumerate(strings):
            if len(string) > self.target_len:
                has_overflow = True
                print(self.fix_string_length(string[0:self.target_len], self.line_size), end='')
                overflow[player] = string[self.target_len:]
            else:
                print(self.fix_string_length(string, self.line_size), end='')
        print()

        while has_overflow:
            has_overflow = False
            for player in range(num_strings):
                if len(overflow[player]) > self.target_len:
                    has_overflow = True
                    print(self.fix_string_length(overflow[player][0:self.target_len], self.line_size), end='')
                    overflow[player] = overflow[player][self.target_len:]
                else:
                    print(self.fix_string_length(overflow[player], self.line_size), end='')
            print()

    def print_lb_list(self, attr, values):
        max_len = max([len(value) for value in values])
        if max_len == 0:
            attr_str = f'{attr}: -'
        else:
            attr_str = f'{attr}:'
        self.print_linebreak([attr_str for _ in range(len(values))])
        for value in values:
            if len(value) < max_len:
                value.extend([''] * (max_len - len(value)))
        values = list(zip(*values))
        for value in values:
            self.print_linebreak(value)

    def print_changes(self):
        changes = []
        for player in self.game.players:
            changes.append(player.str_out.split('\n')[1:])
            player.str_out = ''
        self.print_lb_list('Changes', changes)

    def print_game_state(self, actions, choice=None, ):

        global_attributes = [
            ('Round', lambda: self.game.round_number),
            ('Node', lambda: self.game.game_machine.get_state(self.game.state).name),
            ('Game State', lambda: self.game.game_state),
            ('Current Player', lambda: self.game.current_player),
            ('Locations', lambda: self.game.locations),
        ]

        attributes = [
            ('Player', lambda player: player),
            ('Revealed', lambda player: player.has_revealed()),
            ('Resolved', lambda player: player.has_resolved_conflict),
            ('S', lambda player: player.spice),
            ('$', lambda player: player.solari),
            ('W', lambda player: player.water),
            ('P', lambda player: player.persuasion),
            ('Factions', lambda player: list(map(lambda fac_inf: f"{fac_inf[0].name}: {fac_inf[1]['influence']}", player.factions.items()))),
            ('Available Icons', lambda player: player.icons),
            ('Current Card', lambda player: player.current_card),
            ('Cards', lambda player: player.hand_cards),
            ('Current Plot', lambda player: player.current_intrigue),
            ('Plots', lambda player: player.intrigues),
            ('Played Cards', lambda player: player.played_cards),
            ('Discard Pile', lambda player: player.discard_pile),
            ('Deck', lambda player: player.deck),
            ('Choices', lambda player: player.open_choices),
            ('Decisions', lambda player: player.decided_choices),
            ('Choicing', lambda player: player.current_choicing),
        ]

        current_player_attributes = [
            ('Actions', lambda player: list(map(lambda action: f'{action[0]} - {action[1]}', enumerate(actions))))
        ]
        if choice is not None:
            current_player_attributes.append(('Choice', lambda player: f'{actions[choice]} ({choice})'))
        print('=' * self.max_width)
        print()
        for attr, func in global_attributes:
            print(self.fix_string_length(attr + ': ' + str(func()), self.max_width), end='')
            print()
        print('-' * self.max_width)

        for attr, func in attributes:
            values = []
            is_list = False
            for player in self.game.players:
                attribute = func(player)
                if not isinstance(attribute, list):
                    values.append(attr + ': ' + str(attribute))
                else:
                    is_list = True
                    attr_len = len(f'{attr}: ')
                    values.append(list(map(lambda x: attr_len * ' ' + str(x), attribute)))

            if not is_list:
                self.print_linebreak(values)
            else:
                self.print_lb_list(attr, values)

        for attr, func in current_player_attributes:
            is_list = False
            attribute = func(self.game.current_player)
            if not isinstance(attribute, list):
                values = ['' for _ in range(self.game.num_players)]
                values[self.game.players.index(self.game.current_player)] = attr + ': ' + str(attribute)
            else:
                is_list = True
                attr_len = len(f'{attr}: ')
                list_len = len(attribute)
                values = [[''] * list_len for _ in range(self.game.num_players)]
                values[self.game.players.index(self.game.current_player)] = list(
                    map(lambda x: attr_len * ' ' + str(x), attribute))

            if not is_list:
                self.print_linebreak(values)
            else:
                self.print_lb_list(attr, values)

        print('-' * self.max_width)

    def choose_action(self, actions, move_list, auto):
        invalid_input = True
        while invalid_input and not move_list:
            if auto:
                choice = random.randint(0, len(actions) - 1)
                break
            else:
                choice = input("Choose an action: ")
                try:
                    if choice == 'debug':
                        debug = not debug
                        print(f"Debug mode: {debug}")
                        continue
                    choice = int(choice)
                    if choice < 0 or choice >= len(actions):
                        raise ValueError
                    invalid_input = False
                except ValueError:
                    pass
        if move_list:
            choice = move_list.pop(0)

        choice_str = f'{choice} - {actions[choice]}' + (' (ml)' if move_list else ' (auto)' if auto and not move_list else '')
        self.print_linebreak([choice_str if self.game.current_player == player else '' for player in self.game.players])
        print('-' * self.max_width)
        return choice