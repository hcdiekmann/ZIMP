
from game import Game
from cmd import Cmd


class Console(Cmd):
    """
    Keagan Created class
    """

    def __init__(self, start_coordinates, board_size, card_data, card_image):
        Cmd.__init__(self)
        self.prompt = ">>> "
        self.game = Game(start_coordinates, board_size, card_data, card_image)
        with open("commands.txt", 'r') as file:
            print('Commands: ')
            for lines in file:
                print(f"{lines}")
            print("\n")

    def do_go(self, direction):
        """
        Choose a direction to go from the current room.
        Syntax: go [direction] where direction is either \'N\' (for
        north), \'E\' (for east), \'S\' (for south), \'W\' (for west).

        """
        if not self.game.check_game_state():
            try:
                self.game.player_turn(direction)
            except TypeError as err:
                print(str(err))

    def do_bash(self, direction):
        """
        Choose to bash through a wall.
        """
        self.game.bash_through_wall(direction)

    def do_totem(self, arg):
        """
        Choose to find or burry the totem.
        """
        try:
            self.game.find_or_burry_totem()
        except TypeError as err:
            print(str(err))

    def do_cower(self, arg):
        """
        Choose to curl up into a corner and hide.
        """
        try:
            self.game.cower()
        except TypeError as err:
            print(str(err))

    def do_quit(self, arg):
        """
        Quits the current game.
        """
        print("Goodbye")
        self.game.gui.root.destroy()
        return True

    def do_details(self, args):
        """
        Prints the players details: Location, Health, Attack and Items
        """
        self.game.get_details()

