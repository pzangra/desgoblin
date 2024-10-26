# map_system/map.py

import sys
import os
import random
from collections import Counter
from random import randint
from map_system.tiles import *
from map_system.tiles import default
from battle_system.enemy import generate_enemy

class Map:
    """Class to represent the game map."""

    def __init__(self, width: int, height: int, seed: int = None):
        self.width = width
        self.height = height
        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)


        self.map_data = [[default for _ in range(self.width)] for _ in range(self.height)]
        self.enemies = []
        self.boss_spawned = False
        self.player_pos = (1, 1)
        self.player_previous_tile = self.map_data[self.player_pos[0]][self.player_pos[1]]

        self.create_frame()
        self.fill_default()
        self.generate_patches()
        self.generate_rivers()
        self.place_structures()

    @classmethod
    def generate_map_with_seed(cls, width: int, height: int, seed: int):
        """Generates a map with a specific seed value."""
        return cls(width, height, seed)
    
    def place_player(self, hero):
        """Places the player on the map."""
        x, y = self.player_pos  # Use the initialized player position
        self.map_data[x][y] = player

    def refill_tile(self, x: int, y: int):
        # Logic to refill the tile previously occupied by the player or an enemy
        adjacent_tiles = []

        # Loop to gather adjacent tile types
        for i in range(max(0, x - 1), min(self.height, x + 2)):
            for j in range(max(0, y - 1), min(self.width, y + 2)):
                if (i, j) != (x, y):  # Exclude the current position
                    if self.map_data[i][j] is not None:
                        adjacent_tiles.append(self.map_data[i][j])

        # Find the most common adjacent tile to determine what tile should replace the player's old position
        if adjacent_tiles:
            tile_counts = Counter([tile.symbol_raw for tile in adjacent_tiles])
            most_common_tile_symbol = tile_counts.most_common(1)[0][0]

            # Set the tile object back based on the symbol
            for tile in [plains, forest, mountain, brush, default]:
                if tile.symbol_raw == most_common_tile_symbol:
                    return tile

        # If no adjacent tile or in case of error, return the default tile
        return default

    def create_frame(self):
        """Creates a boundary frame around the map."""
        for x in range(self.height):
            for y in range(self.width):
                if x == 0 or x == self.height - 1:
                    self.map_data[x][y] = Tile("=", "\033[37m")  # Top and bottom borders
                elif y == 0 or y == self.width - 1:
                    self.map_data[x][y] = Tile("|", "\033[37m")  # Left and right borders

    def fill_default(self):
        """Fills the internal part of the map with default tiles."""
        for x in range(1, self.height - 1):
            for y in range(1, self.width - 1):
                self.map_data[x][y] = default

    def generate_patches(self):
        """Generates biome patches on the map."""
        biome_types = [
            (plains, 20, 5, 15),
            (forest, 15, 3, 12),
            (mountain, 10, 4, 10),
            (lake, 7, 4, 8),
            (brush, 12, 3, 10),
            (desert, 10, 4, 12),
            (swamp, 8, 3, 10),
            (snow, 5, 4, 10),
            (hill, 10, 3, 10),
        ]
        for tile, num_patches, min_size, max_size in biome_types:
            self.generate_patch(tile, num_patches, min_size, max_size)

    def generate_patch(self, tile: Tile, num_patches: int, min_size: int, max_size: int):
        """Generates individual patches of a specific biome."""
        for _ in range(num_patches):
            patch_size = randint(min_size, max_size)
            x_start = randint(1, self.height - 2)
            y_start = randint(1, self.width - 2)

            for _ in range(patch_size):
                x_new, y_new = x_start, y_start
                for _ in range(patch_size):
                    direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    x_new = min(max(1, x_new + direction[0]), self.height - 2)
                    y_new = min(max(1, y_new + direction[1]), self.width - 2)

                    if self.map_data[x_new][y_new] == default:
                        self.map_data[x_new][y_new] = tile

    def generate_rivers(self, num_rivers=3):
        """Generates rivers on the map."""
        for _ in range(num_rivers):
            # Start from a random mountain tile or edge of the map
            x = randint(1, self.height - 2)
            y = randint(1, self.width - 2)
            while self.map_data[x][y] != mountain:
                x = randint(1, self.height - 2)
                y = randint(1, self.width - 2)
            # Create a river path
            length = randint(10, 20)
            for _ in range(length):
                self.map_data[x][y] = river
                direction = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                x = min(max(1, x + direction[0]), self.height - 2)
                y = min(max(1, y + direction[1]), self.width - 2)

    def place_structures(self):
        """Places structures like villages on the map."""
        # Place 2 villages on the map
        for _ in range(2):
            while True:
                x = randint(1, self.height - 2)
                y = randint(1, self.width - 2)
                if self.map_data[x][y] == default:
                    self.map_data[x][y] = village
                    break

            # Place caves
        for _ in range(3):
            while True:
                x = randint(1, self.height - 2)
                y = randint(1, self.width - 2)
                if self.map_data[x][y] == mountain:
                    self.map_data[x][y] = cave
                    break
        # Place ruins
        for _ in range(2):
            while True:
                x = randint(1, self.height - 2)
                y = randint(1, self.width - 2)
                if self.map_data[x][y] == plains:
                    self.map_data[x][y] = ruins
                    break

    def display_map(self, hero=None):
        """Displays the map along with the hero's stats."""
        self.clear_screen()
        print(f"Seed: {self.seed}")  # Display seed for reproducibility
        print(f"Hero HP: {hero.health}/{hero.health_max} | Weapon: {hero.weapon.get_display_name()} (Damage: {hero.weapon.damage}) | Cash: {hero.cashpile}")
        for row in self.map_data:
            print("".join([tile.symbol if tile is not None else default.symbol for tile in row]))
        # Display tile type and coordinates
        x, y = hero.player_pos
        tile = self.map_data[x][y]
        tile_name = self.get_tile_name(tile)
        print(f"\nYou are standing on {tile_name} at position ({x}, {y})")
    
    def clear_screen(self):
        """Clears the console screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def update_player_position(self, old_x, old_y, new_x, new_y):
        """Updates the player's position on the map."""
        self.map_data[old_x][old_y] = self.player_previous_tile  # Restore the tile under the player
        # Save the underlying tile before moving the player
        self.player_previous_tile = self.map_data[new_x][new_y]
        self.map_data[new_x][new_y] = player
        self.player_pos = (new_x, new_y)

    def select_enemies(self, boss_defeated, cycle):
        """Selects a list of enemies to place on the map."""
        level_multiplier = 1 + (boss_defeated * 0.2) + (cycle * 0.2)
        enemies_list = []
        for _ in range(6):
            enemy = generate_enemy("low", cycle)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)
        for _ in range(4):
            enemy = generate_enemy("mid", cycle)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)
        for _ in range(2):
            enemy = generate_enemy("high", cycle)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)
        return enemies_list

    def clear_map(self):
        """Clears the current map."""
        self.map_data = [[default for _ in range(self.width)] for _ in range(self.height)]
        self.create_frame()
        self.fill_default()
        self.generate_patches()
        self.place_structures()
        self.enemies = []
        self.boss_spawned = False

    def get_tile_name(self, tile: Tile) -> str:
        """Returns a friendly name for a given tile."""
        tile_names = {
            plains.symbol_raw: "Plains",
            forest.symbol_raw: "Forest",
            brush.symbol_raw: "Brush",
            mountain.symbol_raw: "Mountain",
            water.symbol_raw: "Water",
            lake.symbol_raw: "Lake",
            desert.symbol_raw: "Desert",
            swamp.symbol_raw: "Swamp",
            snow.symbol_raw: "Snow",
            hill.symbol_raw: "Hill",
            river.symbol_raw: "River",
            beach.symbol_raw: "Beach",
            cave.symbol_raw: "Cave",
            ruins.symbol_raw: "Ruins",
            shrine.symbol_raw: "Shrine",
            default.symbol_raw: "Plains",
            village.symbol_raw: "Village",
            'v': "Visited Village",
            'E': "Enemy",
            'P': "Player",
        }
        return tile_names.get(tile.symbol_raw, "Unknown")

    def is_tile_empty(self, x, y):
        """Check if a tile is empty and suitable for enemy placement."""
        tile = self.map_data[x][y]
        # A tile is empty if it's walkable and not occupied by 'E' or 'P'
        return tile.walkable and tile.symbol_raw not in ['E', 'P']

    def place_enemies_on_map(self, enemies_list):
        """Places enemies on the map."""
        for enemy in enemies_list:
            while True:
                x = randint(1, self.height - 2)
                y = randint(1, self.width - 2)
                if self.is_tile_empty(x, y):
                    enemy.pos = (x, y)
                    enemy.underlying_tile = self.map_data[x][y]
                    # Place enemy tile
                    enemy_tile = Tile("E", ansi_colors['red'], walkable=False)
                    self.map_data[x][y] = enemy_tile
                    self.enemies.append(enemy)
                    break