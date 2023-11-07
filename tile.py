# --------------------------------------------------------------
# tile.py
# --------------------------------------------------------------
# Author: Christian Diekmann
#
# Description:
# A tile is a single square on the game board.
# It has a name, an image, and exits to other tiles.
# Also has a tile type determined by the deck it belongs to.
# ---------------------------------------------------------------
class Tile:
    """A tile is a single square on the game board."""

    def __init__(self, image, name, exits, tile_type):
        self.image = image
        self.name = name
        self.exits = exits
        self.tile_type = tile_type

    def __str__(self):
        """Representation of the tile name and exits in ASCII art format."""
        max_name_len = max(
            15, len(self.name))  # Adjust to the length of the longest name
        padded_name = self.name.center(max_name_len)  # Center the name

        top_exit = ' ' if self.exits['N'] else '_'
        right_exit = ' ' if self.exits['E'] else '|'
        bottom_exit = ' ' if self.exits['S'] else '_'
        left_exit = ' ' if self.exits['W'] else '|'

        tile_str = f" {top_exit * (max_name_len + 2)} \n"
        tile_str += f"+{' ' * (max_name_len + 2)}+\n"
        tile_str += f"{left_exit} {padded_name} {right_exit}\n"
        tile_str += f"+{bottom_exit * (max_name_len + 2)}+\n"
        return tile_str

    def possible_exits(self):
        """List of possible exits from the tile."""
        return [d for d, is_exit in self.exits.items() if is_exit]

    def add_exit(self, direction: str) -> None:
        """Add an exit in the given direction to the tile.

        Args:
            direction (str): A cardinal direction, 'N', 'E', 'S', or 'W'

        Raises:
            ValueError: if direction is not a valid cardinal direction
        """
        if direction in 'NESW':
            self.exits[direction] = True
        else:
            raise ValueError(f"{direction} is not a valid exit direction")

    def rotate(self, entry: str, exit: str) -> 'Tile':
        """Rotate tile to align the chosen entry with the chosen exit.

        Args:
            entry (str): the direction of the entry
            exit (str): the direction of the exit
        Returns:
            Tile: the rotated tile
        """
        rotations = {'N': {'N': 2, 'E': 1, 'S': 0, 'W': 3},
                     'E': {'N': 3, 'E': 2, 'S': 1, 'W': 0},
                     'S': {'N': 0, 'E': 3, 'S': 2, 'W': 1},
                     'W': {'N': 1, 'E': 0, 'S': 3, 'W': 2}
                     }[exit][entry]

        for _ in range(rotations):
            self.exits = {direction: self.exits[prev_dir]
                          for direction, prev_dir in zip('NESW', 'WNES')}
            self.image = self.image.rotate(-90)

        return self
