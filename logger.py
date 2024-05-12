class Logger:
    def __init__(self, game: 'Game'):
        self.game = game
        self.max_width = 300
        self.cols = 3
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

        self.print_lb_list('Changes', changes)

    def print_game_state(self, actions, choice=None):

        global_attributes = [
            ('State', lambda: self.game.game_machine.get_state(self.game.state).name),
            ('Current Player', lambda: self.game.current_player),
        ]

        attributes = [
            ('S', lambda player: player.spice),
            ('$', lambda player: player.solari),
            ('P', lambda player: player.persuasion),
            ('Available Icons', lambda player: player.icons),
            ('Current Card', lambda player: player.current_card),
            ('Cards', lambda player: player.hand_cards),
            ('Current Plot', lambda player: player.current_plot),
            ('Plots', lambda player: player.hand_plot_cards),
            ('Played Cards', lambda player: player.played_cards),
            ('Discard Pile', lambda player: player.discard_pile),
            ('Deck', lambda player: player.deck),
        ]

        current_player_attributes = [
            ('Actions', lambda player: list(map(lambda action: f'{action[0]} - {action[1]}', enumerate(actions))))
        ]
        if choice is not None:
            current_player_attributes.append(('Choice', lambda player: f'{actions[choice]} ({choice})'))

        print('=' * self.max_width)
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