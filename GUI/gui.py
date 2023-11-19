# --------------------------------------------------------------
# gui.py
# --------------------------------------------------------------
# Author: Christian Diekmann
#
# Description:
# A GUI for the Zombie in my Pocket game.
# ---------------------------------------------------------------
import tkinter as tk
from PIL import ImageTk
from game_observer import GameObserver


class GUI(GameObserver):
    """Displays the board and player information."""

    def __init__(self, root=None, board_size=(7, 7), tile_size=120):
        self.root = root if root else tk.Tk()
        self.root.title("Zombie in my pocket")
        self.images = []
        cols, rows = board_size
        self.tile_size = tile_size

        self.main_frame = self.create_frame(self.root, fill=tk.BOTH, expand=1)
        self.canvas_frame = self.create_frame(
            self.main_frame, side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas = self.create_canvas(
            self.canvas_frame, side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.scrollbar_y = self.create_scrollbar(
            self.canvas_frame, "vertical", self.canvas.yview, side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x = self.create_scrollbar(
            self.main_frame, "horizontal", self.canvas.xview, side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(
            yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)

        self.frame_group1 = self.create_frame(self.root, side=tk.LEFT, padx=20)
        self.frame_group2 = self.create_frame(self.root, side=tk.LEFT, padx=60)

        self.label_time = self.create_label(self.frame_group1, text="Time: ")
        self.label_dev_cards = self.create_label(
            self.frame_group1, text="Development Cards: ")
        self.lable_outdoor_tiles = self.create_label(
            self.frame_group1, text="Outdoor Tiles: ")
        self.lable_indoor_tiles = self.create_label(
            self.frame_group1, text="Indoor Tiles: ")

        self.lable_health = self.create_label(
            self.frame_group2, text="Health: ")
        self.lable_attack = self.create_label(
            self.frame_group2, text="Attack: ")
        self.items = self.create_label(self.frame_group2, text="Items: ")

        self.frame_inside_canvas = self.create_frame(self.canvas, anchor="nw")
        self.canvas.create_window(
            (0, 0), window=self.frame_inside_canvas, anchor="nw")

        self.grid_rects = [[None for _ in range(cols)] for _ in range(rows)]
        for i in range(rows):
            for j in range(cols):
                self.grid_rects[i][j] = self.canvas.create_rectangle(
                    j * self.tile_size, i * self.tile_size,
                    (j + 1) * self.tile_size, (i + 1) * self.tile_size)

        self.frame_inside_canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", self._on_shiftmousewheel)

    # Factory methods
    def create_label(self, parent, text, **pack_options):
        label = tk.Label(parent, text=text)
        label.pack(**pack_options)
        return label

    def create_frame(self, parent, **pack_options):
        frame = tk.Frame(parent)
        frame.pack(**pack_options)
        return frame

    def create_canvas(self, parent, **pack_options):
        canvas = tk.Canvas(parent)
        canvas.pack(**pack_options)
        return canvas

    def create_scrollbar(self, parent, orient, command, **pack_options):
        scrollbar = tk.Scrollbar(parent, orient=orient, command=command)
        scrollbar.pack(**pack_options)
        return scrollbar

    # Event handlers
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta//120), "units")

    def _on_shiftmousewheel(self, event):
        self.canvas.xview_scroll(-1*(event.delta//120), "units")

    def place_tile(self, tile, row, col):
        """Places a tile on the board at the given row and column.
        """
        tile_image = tile.image
        tile_image = tile_image.resize((self.tile_size, self.tile_size))
        tile_tk_image = ImageTk.PhotoImage(tile_image)
        self.canvas.create_image(
            col * self.tile_size, row * self.tile_size,
            image=tile_tk_image, anchor=tk.NW)
        self.images.append(tile_tk_image)

    # Observer methods
    def update_dev_cards(self, cards_count, current_time):
        """Updates the development cards and time labels.
        """
        self.label_time.config(text=f"Time: {current_time}")
        self.label_dev_cards.config(text=f"Development Cards: {cards_count}")

    def update_tile_count(self, indoor_count, outdoor_count):
        """Updates the indoor and outdoor tile count labels.
        """
        self.lable_outdoor_tiles.config(
            text=f"Outdoor Tiles: {outdoor_count}")
        self.lable_indoor_tiles.config(
            text=f"Indoor Tiles: {indoor_count}")

    def update_player_info(self, health, attack, items, location):
        """Updates the player information labels and moves the player marker.
        """
        self.lable_health.config(text=f"Health: {health}")
        self.lable_attack.config(text=f"Attack: {attack}")
        self.items.config(text=f"Items: {items}")
        self._draw_player(*location)

    def _draw_player(self, row, col):
        """Draws the player marker on the board.
        """
        # Remove the previous player marker (if it exists)
        if hasattr(self, 'player_marker'):
            self.canvas.delete(self.player_marker)

        # one-eighth the tile size
        marker_size = self.tile_size // 8
        self.player_marker = self.canvas.create_oval(
            col * self.tile_size + 3 * marker_size,
            row * self.tile_size + 3 * marker_size,
            (col + 1) * self.tile_size - 3 * marker_size,
            (row + 1) * self.tile_size - 3 * marker_size,
            fill="red")
