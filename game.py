from board import Board
from player import Player
from GUI.gui import GUI


class Game:
    """
    The Game class controls the game logic eg (movement, attack)
    """

    def __init__(self, start_coordinates, board_size, card_data, card_image):
        self.player = Player(start_coordinates)
        self.board = Board(start_coordinates, card_data, card_image)
        self.gui = GUI(board_size)
        self.completed_turn_sequence = False
        self._setup(start_coordinates)

    def _setup(self, start_coordinates):
        self.gui.place_tile(self.board.foyer_tile, *start_coordinates)
        self._update_gui_labels()
        self._print_current_room()

    def get_details(self):
        print(self.player.get_details())

    def _update_gui_labels(self):
        self.gui.update_dev_cards(
            self.board.dev_cards.count, self.board.time)
        self.gui.update_tile_count(
            self.board.indoor_tiles.count, self.board.outdoor_tiles.count)
        self.gui.update_player_info(
            self.player.health, self.player.attack, self.player.items,
            self.player.location)

    def _print_current_room(self):
        print(f"You are in the {self._current_room().name}.")
        print(self._current_room().__str__())
        print(f"Possible directions: {self._current_room().possible_exits()}")

    def _current_room(self):
        return self.board.tile_map[self.player.location]

    def _move_direction(self, direction):
        """
        Returns the new location if the direction is valid
        """
        possible_exits = self._current_room().possible_exits()
        if direction not in possible_exits:
            print(
                f"Invalid direction. Choose from: {possible_exits}")
            return None
        else:
            return self._update_location(direction)

    def player_turn(self, direction):
        """
        Move the player in the chosen direction.
        """
        dir = direction.upper()
        new_location = self._move_direction(dir)
        if new_location is None:
            return
        if self.board.is_explored(new_location):
            room = self.board.tile_map[new_location]
            if self._opposite_direction(dir) not in room.possible_exits():
                print("This exit is blocked by a wall from another room.")
                return
            self.player.location = new_location
            self._resolve_dev_card()
        else:
            new_tile, tile_type = self.board.draw_tile(self._current_room())
            if new_tile is None:
                print(f"No more {tile_type} to draw.")
                return
            self.player.location = new_location
            self.gui.place_tile(new_tile, *new_location)
            self._place_new_tile(dir, new_tile)

        self.completed_turn_sequence = True

    def _place_new_tile(self, chosen_exit, new_tile):
        """
        Place a newly explored room on the board.
        """
        possible_entries = new_tile.possible_exits()
        if len(possible_entries) > 1:
            if new_tile.name == 'Dining Room':
                # dining room always placed with exit to patio 'N'
                new_tile = self._place_patio_tile(chosen_exit, new_tile)
            else:
                new_tile = self._choose_entry(
                    chosen_exit, new_tile, possible_entries)
        else:
            new_tile = new_tile.rotate(
                possible_entries[0], chosen_exit)

        self.gui.place_tile(new_tile, *self.player.location)
        self.board.tile_map[self.player.location] = new_tile
        print(new_tile.__str__())
        self._resolve_dev_card()

    def _choose_entry(self, chosen_exit, new_tile, possible_entries):
        """
        Choose side to enter new room from.
        Rotate the new tile accordingly.
        """
        print(
            f"You found the {new_tile.name}, enter from: {possible_entries}")
        chosen_entry = ""
        while chosen_entry not in possible_entries:
            chosen_entry = input("Choose a side to enter from: ").upper()
            if chosen_entry not in possible_entries:
                print(f"Invalid entry. Please choose from: {possible_entries}")

        return new_tile.rotate(chosen_entry, chosen_exit)

    def _place_patio_tile(self, chosen_exit, dining_room):
        """
        Places patio tile below or above the dining room.
        """
        patio = self.board.patio_tile
        x, y = self.player.location
        if chosen_exit == 'S':
            # flip dining room as N is reserved for patio
            dining_room = dining_room.rotate('S', 'S')
            x += 1  # patio below dining room
        else:
            patio = patio.rotate('N', 'N')
            x -= 1  # patio above dining room
        patio_location = (x, y)
        self.gui.place_tile(patio, *patio_location)
        self.board.tile_map[patio_location] = patio
        return dining_room

    def _resolve_dev_card(self):
        """
        Handle logic for resolving a development card.
        """
        runaway = False
        card = self.board.dev_cards.draw()
        card.display(self.board.time)
        content = card.content[self.board.time]
        if content['text'] == 'zombies':
            runaway = self._runaway_or_fight(content['value'])
        elif content['text'] == 'ITEM':
            self._get_new_item()
        else:
            self.player.health += content['value']

        if not self._game_over() and not runaway:
            room = self._current_room()
            if room.name == 'Kitchen' or room.name == 'Garden':
                self.player.health += 1
            elif room.name == 'Storage':
                self._get_new_item()

        self._print_current_room()
        self._update_gui_labels()
        return

    def _runaway_or_fight(self, num_zombies):
        """
        handle logic for running away or fighting
        """
        self._update_gui_labels()
        possible_actions = ['F', 'R']
        print("Enter 'F' to fight or 'R' to run away.")
        action = ""
        while action not in possible_actions:
            action = input("Choose your action: ").upper()
            if action not in possible_actions:
                print(f"Invalid, choose: {possible_actions}")

        if action == 'R':
            self._escape_zombies()
            return True

        self._fight_zombies(num_zombies)
        return False

    def _escape_zombies(self):
        """
        Escape zombies to a previously explored room.
        """
        directions = self._current_room().possible_exits()
        escape_directions = []
        for dir in directions:
            location = self._update_location(dir)
            if self.board.is_explored(location):
                escape_directions.append(dir)

        print(f"Possible escape directions: {escape_directions}")
        chosen_dir = ""
        while chosen_dir not in escape_directions:
            chosen_dir = input("Choose your escape direction: ").upper()
            if chosen_dir not in escape_directions:
                print(
                    "Invalid direction. You can only escape to previously "
                    f"explored rooms. Please choose from: {escape_directions}")
        self.player.location = self._update_location(chosen_dir)

        if 'Oil' in self.player.items:
            self.player.items.remove('Oil')
            return
        self.player.health -= 1

    def _fight_zombies(self, num_zombies):
        """
        Fight zombies, take damage if attack is not enough.
        """
        damage = num_zombies - self.player.attack
        if damage >= 0:
            damage = min(damage, 4)  # max damage is 4
            self.player.take_damage(damage)

    def _get_new_item(self):
        """
        Logic for getting new items
        """
        possible_actions = ["Y", "N"]
        action = ""
        if not self._game_over():
            item = self.board.dev_cards.draw().content['Item']
            new_item = item['text']

            print(f"You found {new_item}")
            if len(self.player.items) >= 2:
                while action not in possible_actions:
                    action = input(
                        "Do you want to replace an item? (Y/N): ").upper()
                    print(f"Your current items: {self.player.items}")
                    if action not in possible_actions:
                        print(f"Invalid choice, choose: {possible_actions}")
                    if action == 'Y':
                        self.replace_item(new_item)
                        self._update_attack(new_item)
            else:
                self.player.items.append(new_item)
                self._update_attack(new_item)

    def _update_attack(self, item):
        """Update the attack score based on the items inventory
        """
        if item == 'Soda Can':
            self.player.health += 2
        if item == 'Golf Club' or 'Grisly Femur' or 'Board with Nails':
            self.player.attack += 1
        if item == 'Machete':
            self.player.attack += 2
        if item == 'Chainsaw':
            self.player.attack += 3

    def replace_item(self, new_item):
        """
        This function does the logic for replacing items
        if the player wants to
        """
        item_to_replace = ""
        while item_to_replace not in self.player.items:
            item_to_replace = input("Choose an item to replace: ")
            if item_to_replace in self.player.items:
                self.player.items.remove(item_to_replace)
                self.player.items.append(new_item)
                print(f"You replaced {item_to_replace} with {new_item}.")
                return
            else:
                print("Invalid item choice.")

    def cower(self):
        if not self.completed_turn_sequence:
            print('You need to complete a turn sequence before cowering')
            return
        self.completed_turn_sequence = False
        self.player.health += 3
        self.board.dev_cards.draw()
        self._update_gui_labels()
        if not self._game_over():
            self._print_current_room()
        return

    def bash_through_wall(self, direction):
        """
        Logic for bashing through a wall.
        """
        if not self.completed_turn_sequence:
            print("You can't bash afer after cowering.")
            return

        valid_directions = ['N', 'E', 'S', 'W']
        dir = direction.upper()

        if dir not in valid_directions:
            print("Invalid direction. Please enter 'N', 'E', 'S', or 'W'.")
            return

        if dir in self._current_room().possible_exits():
            print(
                f"No need to bash. A valid exit exists, use 'go {dir}'"
                "commmand.")
            return

        current_room = self._current_room()
        new_location = self._update_location(dir)
        if self.board.is_explored(new_location):
            new_room = self.board.tile_map[new_location]
            if self._opposite_direction(dir) not in new_room.possible_exits():
                new_room.add_exit(self._opposite_direction(dir))
            current_room.add_exit(dir)
            self.player.location = new_location
            self._fight_zombies(3)
            # self._resolve_dev_card() # Also resolve a dev card??
        else:
            new_tile, tile_type = self.board.draw_tile(current_room)
            if new_tile is None:
                print(
                    f"Can't bash from {tile_type}, no more rooms to explore.")
                return
            current_room.add_exit(dir)
            self.player.location = new_location
            self.gui.place_tile(new_tile, *new_location)
            self._fight_zombies(3)
            self._place_new_tile(dir, new_tile)

        if not self._game_over():
            pass

    def find_or_burry_totem(self):
        room = self._current_room()
        if room.name == 'Evil Temple':
            self._find_totem()
        elif room.name == 'Graveyard':
            self._burry_totem()
        else:
            print("You are not in the right room!")
        return

    def _find_totem(self):
        print("You are searching for the Totem!")
        self._resolve_dev_card()
        if not self._game_over():
            self.player.has_totem = True
            print("You found the Totem!")

    def _burry_totem(self):
        if not self.player.has_totem:
            print("You don't have the Totem!")
            return
        print("You are burying the Totem!")
        self._resolve_dev_card()
        if not self._game_over():
            print("All zombies collapse. You WIN!")

    def _game_over(self):
        """
        Check if the game is over.
        """
        if self.board.dev_cards.count == 0:
            if self.board.time == "11 PM":
                print("You ran out of time. GAME OVER!")
                return True
            self.board.update_time()

        if self.player.health <= 0:
            print("You died. GAME OVER!")
            return True

        self._update_gui_labels()
        return False

    def _opposite_direction(self, direction):
        """
        Return the opposite cardinal direction.
        """
        opposites = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
        return opposites.get(direction, "Invalid direction")

    def _update_location(self, direction):
        """
        Calculate the new location based on the chosen direction.
        """
        x, y = self.player.location
        if direction == 'E':
            return x, y + 1
        elif direction == 'W':
            return x, y - 1
        elif direction == 'N':
            return x - 1, y
        elif direction == 'S':
            return x + 1, y
