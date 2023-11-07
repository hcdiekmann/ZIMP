# --------------------------------------------------------------
# tile_deck.py
# --------------------------------------------------------------
# Author: Christian Diekmann
#
# Description:
# A deck of tiles represented as a Python class.
# Using Template method design pattern
# ---------------------------------------------------------------
import json
from abc import ABC, abstractmethod
from typing import List
from random import shuffle
from PIL import Image, UnidentifiedImageError
from tile import Tile


class TileDeck(ABC):

    def __init__(self):
        self.tiles = self._initialize_tiles()
        self.count = len(self.tiles)

    @property
    @abstractmethod
    def deck_name(self) -> str:
        """The type/name of the deck, to be defined by subclasses."""
        pass

    @property
    @abstractmethod
    def _metadata_path(self) -> str:
        """The path to the metadata file, to be defined by subclasses."""
        pass

    @property
    @abstractmethod
    def _image_path(self) -> str:
        """The path to the image file, to be defined by subclasses."""
        pass

    @property
    def _num_rows_in_img(self) -> int:
        """The number of rows of tiles in the image."""
        return 2

    @property
    def _num_cols_in_img(self) -> int:
        """The number of columns of tiles in the image."""
        return 4

    def _initialize_tiles(self) -> List[Tile]:
        """Creates and initializes tiles from the image and metadata.

        Returns:
            List[Tile]: The list of tiles in the deck
        """
        image = self._load_image()
        tile_width, tile_height = self._get_tile_dimensions(image)
        tile_metadata = self._load_metadata()

        tiles = [
            self._create_tile(
                self._crop_tile_image(
                    image, i, j, tile_width, tile_height
                ),
                tile_metadata[str(index)]
            )  # generator expression
            for index, (i, j) in enumerate(self._iterate_tile_positions(),
                                           start=1)
        ]
        shuffle(tiles)
        return tiles

    def _get_tile_dimensions(self, image) -> tuple:
        tile_width = image.width // self._num_cols_in_img
        tile_height = image.height // self._num_rows_in_img
        return tile_width, tile_height

    def _iterate_tile_positions(self) -> tuple:
        for i in range(self._num_rows_in_img):
            for j in range(self._num_cols_in_img):
                yield i, j

    def _crop_tile_image(self, image, i, j, tile_width, tile_height) -> Image:
        left = j * tile_width
        top = i * tile_height
        right = (j + 1) * tile_width
        bottom = (i + 1) * tile_height
        return image.crop((left, top, right, bottom))

    def _create_tile(self, tile_image, metadata) -> Tile:
        return Tile(tile_image, metadata['name'],
                    metadata['exits'], self.deck_name)

    def _load_metadata(self) -> dict:
        try:
            with open(self._metadata_path, 'r') as file:
                tile_metadata = json.load(file)
        except FileNotFoundError as e:
            raise TileDeckInitializationError(
                f"File {self._metadata_path} not found.") from e
        except json.JSONDecodeError as e:
            raise TileDeckInitializationError(
                f"Error decoding JSON from {self._metadata_path}.") from e

        self._validate_metadata(tile_metadata)
        return tile_metadata

    def _validate_metadata(self, metadata):
        for index, tile in metadata.items():
            if 'name' not in tile or 'exits' not in tile:
                raise TileDeckInitializationError(
                    f"Invalid metadata for tile {index} in "
                    f"{self._metadata_path}. "
                    f"Make sure that each tile has a 'name' and 'exits' key.")

    def _load_image(self) -> Image:
        try:
            image = Image.open(self._image_path)
        except FileNotFoundError as e:
            raise TileDeckInitializationError(
                f"Tile image file {self._image_path} not found.") from e
        except UnidentifiedImageError as e:
            raise TileDeckInitializationError(
                f"Invalid tile image for file {self._image_path}.") from e

        return image

    def draw_by_name(self, name) -> Tile:
        """Draws a tile from the deck by name.

        Args:
            name (str): The name of the tile to be drawn

        Returns:
            Tile: The tile if found else None
        """
        for i, tile in enumerate(self.tiles):
            if tile.name == name:
                self.count -= 1
                return self.tiles.pop(i)
        return None

    def draw(self) -> Tile:
        """Draws a tile from the top of the deck."""
        if self.count > 0:
            tile = self.tiles.pop(0)
            self.count -= 1
            return tile
        return None


class TileDeckInitializationError(Exception):
    pass


class IndoorTileDeck(TileDeck):
    """A deck of indoor tiles."""
    @property
    def deck_name(self) -> str:
        return "Indoor"

    @property
    def _metadata_path(self) -> str:
        return "assets/indoor_tiles.json"

    @property
    def _image_path(self) -> str:
        return "assets/indoor_tiles.jpg"


class OutdoorTileDeck(TileDeck):
    """A deck of outdoor tiles."""
    @property
    def deck_name(self) -> str:
        return "Outdoor"

    @property
    def _metadata_path(self) -> str:
        return "assets/outdoor_tiles.json"

    @property
    def _image_path(self) -> str:
        return "assets/outdoor_tiles.jpg"


if __name__ == '__main__':
    # Example usage:
    indoor_tiles = IndoorTileDeck()
    print(f"Indoor tile count: {indoor_tiles.count}")
    bathroom_tile = indoor_tiles.draw_by_name('Bathroom')
    print(bathroom_tile.exits)
    tile = indoor_tiles.draw()
    print(f"Random tile: {tile.name}")
    print(f"Indoor tile count: {indoor_tiles.count}")
