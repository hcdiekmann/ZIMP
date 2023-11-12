import unittest
import json
from unittest.mock import mock_open, patch
from tile_deck import TileDeck, OutdoorTileDeck, IndoorTileDeck, \
    TileDeckInitializationError, DeckConfig
from tile import Tile
from PIL import Image, UnidentifiedImageError


class TestTileDeckImpl(TileDeck):
    def _generate_deck_config(self):
        # Provide a simple implementation for testing
        return DeckConfig(
            metadata_path="assets/outdoor_tiles.json",
            image_path="assets/outdoor_tiles.jpg",
            deck_name="TestDeck",
            num_cols_in_img=4,
            num_rows_in_img=2
        )


class TestTileDeck(unittest.TestCase):
    def test_generate_deck_config(self):
        # Instantiate the test-specific subclass
        test_deck = TestTileDeckImpl()

        # Test if the config is generated correctly
        config = test_deck.config
        self.assertIsNotNone(config)
        self.assertEqual(config.deck_name, 'TestDeck')
        self.assertEqual(config.num_cols_in_img, 4)
        self.assertEqual(config.num_rows_in_img, 2)


class TestConcreteTileDeck(unittest.TestCase):

    def setUp(self):
        self.tile_deck = OutdoorTileDeck()
        self.indoor_tile_deck = IndoorTileDeck()

    def test_init(self):
        self.assertIsNotNone(self.tile_deck._tiles)
        self.assertEqual(self.tile_deck.count, len(self.tile_deck._tiles))

    def test_initialize_tiles(self):
        self.tile_deck._tiles = self.tile_deck._initialize_tiles()
        self.assertGreater(len(self.tile_deck._tiles), 0)
        self.assertIsInstance(self.tile_deck._tiles[0], Tile)

    def test_get_tile_dimensions(self):
        mock_image = Image.new('RGB', (100, 100))
        tile_width, tile_height = self.tile_deck._get_tile_dimensions(
            mock_image)
        expected_width = 100 // self.tile_deck.config.num_cols_in_img
        expected_height = 100 // self.tile_deck.config.num_rows_in_img
        self.assertEqual(tile_width, expected_width)
        self.assertEqual(tile_height, expected_height)

    def test_iterate_tile_positions(self):
        positions = list(self.tile_deck._iterate_tile_positions())
        expected_num_positions = self.tile_deck.config.num_rows_in_img * \
            self.tile_deck.config.num_cols_in_img
        self.assertEqual(len(positions), expected_num_positions)
        self.assertEqual(len(positions), len(set(positions)))

    def test_crop_tile_image(self):
        mock_image = Image.new('RGB', (100, 100))
        tile_image = self.tile_deck._crop_tile_image(
            mock_image, 0, 0, 50, 50)
        self.assertEqual(tile_image.size, (50, 50))

    def test_load_metadata(self):
        metadata = self.tile_deck._load_metadata()
        self.assertIsNotNone(metadata)
        self.assertEqual(len(metadata), self.tile_deck.config.num_rows_in_img *
                         self.tile_deck.config.num_cols_in_img)
        self.assertIsInstance(metadata, dict)
        self.assertIn('0', metadata)
        self.assertIn('name', metadata['0'])
        self.assertIn('exits', metadata['0'])

    def test_create_tile(self):
        mock_image = Image.new('RGB', (100, 100))
        metadata = {
            'name': 'Test',
            'exits': [True, False, True, False]
        }
        tile = self.tile_deck._create_tile(mock_image, metadata)
        self.assertIsInstance(tile, Tile)
        self.assertEqual(tile.name, 'Test')
        self.assertEqual(tile.exits, metadata['exits'])
        self.assertEqual(tile.tile_type, self.tile_deck.config.deck_name)

    def test_draw(self):
        initial_count = self.tile_deck.count
        tile = self.tile_deck.draw()
        self.assertIsNotNone(tile)
        self.assertEqual(self.tile_deck.count, initial_count - 1)

    def test_draw_by_name(self):
        tile = self.tile_deck.draw_by_name("Garden")
        self.assertIsNotNone(tile)
        self.assertEqual(tile.name, "Garden")

    def test_draw_empty_deck(self):
        self.tile_deck._tiles = []
        tile = self.tile_deck.draw()
        self.assertIsNone(tile)
        tile = self.tile_deck.draw_by_name("Garden")
        self.assertIsNone(tile)

    def test_load_invalid_metadata(self):
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with self.assertRaises(TileDeckInitializationError) as cm:
                self.tile_deck._load_metadata()
            self.assertIn('Error decoding JSON', str(cm.exception))

    def test_invalid_metadata(self):
        with patch('builtins.open', mock_open(read_data='{"0": {"name": "Test"}}')):
            with self.assertRaises(TileDeckInitializationError) as cm:
                self.tile_deck._load_metadata()
            self.assertIn('Invalid metadata', str(cm.exception))

    def test_file_not_found_load_metadata(self):
        self.tile_deck.config = self.tile_deck.config._replace(
            metadata_path='non_existent.json')
        with self.assertRaises(TileDeckInitializationError) as cm:
            self.tile_deck._load_metadata()
        self.assertIn('File non_existent.json not found', str(cm.exception))

    def test_load_invalid_image(self):
        with patch('PIL.Image.open', side_effect=UnidentifiedImageError):
            self.tile_deck.config = self.tile_deck.config._replace(
                image_path='invalid_tiles.png')
            with self.assertRaises(TileDeckInitializationError) as cm:
                self.tile_deck._load_image()
            self.assertIn('Invalid tile image', str(cm.exception))

    def test_file_not_found_load_image(self):
        self.tile_deck.config = self.tile_deck.config._replace(
            image_path='non_existent.png')
        with self.assertRaises(TileDeckInitializationError) as cm:
            self.tile_deck._load_image()
        self.assertIn(
            'Tile image file non_existent.png not found', str(cm.exception))


if __name__ == '__main__':
    unittest.main()
