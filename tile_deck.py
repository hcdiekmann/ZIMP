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
    """A deck of tiles."""

    def __init__(self):
        self._tiles = self._initialize_tiles()

    @property
    def count(self) -> int:
        return len(self._tiles)

    @abstractmethod
    def deck_name(self) -> str:
        pass

    @abstractmethod
    def metadata_path(self) -> str:
        pass

    @abstractmethod
    def image_path(self) -> str:
        pass

    @abstractmethod
    def num_cols_in_img(self) -> int:
        pass

    @abstractmethod
    def num_rows_in_img(self) -> int:
        pass

    def _initialize_tiles(self) -> List[Tile]:
        """Creates and initializes tiles from the image and metadata.

        Returns:
            List[Tile]: The list of tiles in the deck
        """
        image = self._load_image()
        width, height = self._get_tile_dimensions(image)
        tile_metadata = self._load_metadata()

        tiles = []
        for index, (i, j) in enumerate(self._iterate_tile_positions()):
            tile_image = self._crop_tile_image(
                image, i, j, width, height)
            metadata = tile_metadata[str(index)]
            tile = self._create_tile(tile_image, metadata)
            tiles.append(tile)

        shuffle(tiles)
        return tiles

    def _get_tile_dimensions(self, image: Image) -> tuple:
        tile_width = image.width // self.num_cols_in_img()
        tile_height = image.height // self.num_rows_in_img()
        return tile_width, tile_height

    def _iterate_tile_positions(self) -> tuple:
        for i in range(self.num_rows_in_img()):
            for j in range(self.num_cols_in_img()):
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
        data_path = self.metadata_path()
        try:
            with open(data_path, 'r') as file:
                tile_metadata = json.load(file)
        except FileNotFoundError as e:
            raise TileDeckInitializationError(
                f"File {data_path} not found.") from e
        except json.JSONDecodeError as e:
            raise TileDeckInitializationError(
                f"Error decoding JSON from {data_path}.") from e

        self._validate_metadata(tile_metadata, data_path)
        return tile_metadata

    def _validate_metadata(self, metadata: dict, path: str) -> None:
        for index, tile in metadata.items():
            if 'name' not in tile or 'exits' not in tile:
                raise TileDeckInitializationError(
                    f"Invalid metadata for tile {index} in {path}."
                    f"Make sure that each tile has a 'name' and 'exits' key.")

    def _load_image(self) -> Image:
        path = self.image_path()
        try:
            image = Image.open(path)
        except FileNotFoundError as e:
            raise TileDeckInitializationError(
                f"Tile image file {path} not found.") from e
        except UnidentifiedImageError as e:
            raise TileDeckInitializationError(
                f"Invalid tile image for file {path}.") from e

        return image

    def draw_by_name(self, name: str) -> Tile:
        """Draws a tile from the deck by name.

        Args:
            name (str): The name of the tile to be drawn

        Returns:
            Tile: The tile if found else None
        """
        for i, tile in enumerate(self._tiles):
            if tile.name == name:
                return self._tiles.pop(i)
        return None

    def draw(self) -> Tile:
        """Draws a tile from the top of the deck."""
        if len(self._tiles) > 0:
            return self._tiles.pop(0)
        return None


class TileDeckInitializationError(Exception):
    pass


class IndoorTileDeck(TileDeck):
    """A deck of indoor tiles."""

    def deck_name(self) -> str:
        return "Indoor"

    def metadata_path(self) -> str:
        return "assets/indoor_tiles.json"

    def image_path(self) -> str:
        return "assets/indoor_tiles.jpg"

    def num_cols_in_img(self) -> int:
        return 4

    def num_rows_in_img(self) -> int:
        return 2


class OutdoorTileDeck(TileDeck):
    """A deck of outdoor tiles."""

    def deck_name(self) -> str:
        return "Outdoor"

    def metadata_path(self) -> str:
        return "assets/outdoor_tiles.json"

    def image_path(self) -> str:
        return "assets/outdoor_tiles.jpg"

    def num_cols_in_img(self) -> int:
        return 4

    def num_rows_in_img(self) -> int:
        return 2


if __name__ == '__main__':
    # Example usage:
    indoor_tiles = IndoorTileDeck()
    print(f"Indoor tile count: {indoor_tiles.count}")
    bathroom_tile = indoor_tiles.draw_by_name('Bathroom')
    print(bathroom_tile.exits)
    tile = indoor_tiles.draw()
    print(f"Random tile: {tile.name}")
    print(tile.__str__())
    print(f"Indoor tile count: {indoor_tiles.count}")
