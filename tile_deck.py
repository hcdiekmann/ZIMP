# --------------------------------------------------------------
# tile_deck.py
# --------------------------------------------------------------
# Author: Christian Diekmann
#
# Description:
# A deck of tiles represented as a Python class.
# Using Factory Method and Abstract Base Class design patterns for
# creation and structure of tile decks.
# ---------------------------------------------------------------
import json
import random
from PIL import Image, UnidentifiedImageError
from tile import Tile


class TileDeck:
    """
    A tile deck is a collection of tiles that can be drawn from.
    """
    def __init__(self, deck_type, image_path, metadata_path, img_num_rows=2, img_num_cols=4):
        self.tiles = []
        self.count = 0
        self.image_rows = img_num_rows
        self.image_cols = img_num_cols
        self.deck_type = deck_type
        self.image_path = image_path
        self.metadata_path = metadata_path
        self._initialize_tiles()

    def _initialize_tiles(self) -> None:
        """
        Initializes the list of tiles in the deck from the image and metadata.
        """
        tile_metadata = self._load_metadata(self.metadata_path)
        image = self._load_image(self.image_path)
        tile_width, tile_height = self._get_tile_dimensions(image)

        index = 1
        for i, j in self._iterate_tile_positions():
            tile_image = self._crop_tile_image(
                image, i, j, tile_width, tile_height)
            metadata = tile_metadata[str(index)]
            self._add_tile(tile_image, metadata)
            index += 1

        self._shuffle_tiles()
        self.count = len(self.tiles)

    def _get_tile_dimensions(self, image) -> tuple:
        tile_width = image.width // self.image_cols
        tile_height = image.height // self.image_rows
        return tile_width, tile_height

    def _iterate_tile_positions(self) -> tuple:
        for i in range(self.image_rows):
            for j in range(self.image_cols):
                yield i, j

    def _crop_tile_image(self, image, i, j, tile_width, tile_height) -> Image:
        left = j * tile_width
        top = i * tile_height
        right = (j + 1) * tile_width
        bottom = (i + 1) * tile_height
        return image.crop((left, top, right, bottom))

    def _add_tile(self, tile_image, metadata) -> None:
        tile = Tile(tile_image, metadata['name'],
                    metadata['exits'], self.deck_type)
        self.tiles.append(tile)

    def _shuffle_tiles(self) -> None:
        random.shuffle(self.tiles)

    def _load_metadata(self, metadata_path) -> dict:
        try:
            with open(metadata_path, 'r') as file:
                tile_metadata = json.load(file)
        except FileNotFoundError as e:
            raise TileDeckInitializationError(
                f"File {metadata_path} not found.") from e
        except json.JSONDecodeError as e:
            raise TileDeckInitializationError(
                f"Error decoding JSON from {metadata_path}.") from e

        # check that name and exits are present in the metadata
        for tile in tile_metadata.values():
            if 'name' not in tile or 'exits' not in tile:
                raise TileDeckInitializationError(
                    f"Invalid metadata in {metadata_path}. Make sure that "
                    f"each tile has a 'name' and 'exits' key.")
        return tile_metadata

    def _load_image(self, image_path) -> Image:
        try:
            image = Image.open(image_path)
        except FileNotFoundError as e:
            raise TileDeckInitializationError(
                f"Tile image file {image_path} not found.") from e
        except UnidentifiedImageError as e:
            raise TileDeckInitializationError(
                f"Invalid tile image for file {image_path}.") from e

        return image

    def draw_by_name(self, name) -> Tile:
        """Draws a tile from the deck by name

        Args:
            name (str): The name of the tile to be drawn

        Returns:
            Tile: The tile with the given name
        """
        for i, tile in enumerate(self.tiles):
            if tile.name == name:
                self.count -= 1
                return self.tiles.pop(i)
        return None

    def draw(self) -> Tile:
        """
        Draws a tile from the deck.
        """
        if self.count > 0:
            tile = self.tiles.pop(0)
            self.count -= 1
            return tile
        return None


class TileDeckInitializationError(Exception):
    pass


if __name__ == '__main__':
    # Create a deck of indoor and outdoor tiles
    indoor_deck = TileDeck('Indoor', 'assets/indoor_tiles.jpg', 'assets/indoor_tiles.json')
    outdoor_deck = TileDeck('Outdoor', 'assets/outdoor_tiles.jpg', 'assets/outdoor_tiles.json')

    print(f"Indoor deck count: {indoor_deck.count}")
    print(f"Outdoor deck count: {outdoor_deck.count}")

    # Draw a specific tile from the indoor deck
    indoor_tile = indoor_deck.draw_by_name('Bathroom')
    print(f"Indoor tile: {indoor_tile.name}")
    print(f"Bathroom exits: {indoor_tile.exits}")

    # Check if the tile is from the indoor or outdoor deck
    print(f"Is indoor tile: {indoor_tile.tile_type == 'Indoor'}")
    print(f"Is outdoor tile: {indoor_tile.tile_type == 'Outdoor'}")

    # Draw a specific tile from the outdoor deck
    outdoor_tile = outdoor_deck.draw_by_name('Graveyard')
    print(f"Outdoor tile: {outdoor_tile.name}")
    print(f"Graveyard exits: {outdoor_tile.exits}")

    # Draw a tile from the indoor deck
    indoor_tile = indoor_deck.draw()
    # Draw a tile from the outdoor deck
    outdoor_tile = outdoor_deck.draw()

    print(f"Indoor tile: {indoor_tile.name}")
    print(f"Outdoor tile: {outdoor_tile.name}")

    print(f"Indoor deck count: {indoor_deck.count}")
    print(f"Outdoor deck count: {outdoor_deck.count}")
