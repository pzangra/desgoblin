# map_system/map.py

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from collections import Counter
from random import randint

from map_system.tiles import *
from battle_system.enemy import generate_enemy

class Map:
    """Class to represent the game map."""
    TILE_SIZE = 16

    def __init__(self, screen: pygame.Surface, width: int, height: int, seed: int = None):
        self.width = width
        self.height = height
        self.screen = screen

        # Confirm that self.screen is a Surface
        assert isinstance(self.screen, pygame.Surface), "screen should be a Pygame Surface"

        self.seed = seed if seed is not None else random.randint(0, 1000000)
        random.seed(self.seed)

        self.map_data = [[default for _ in range(self.width)] for _ in range(self.height)]
        self.enemies = []
        self.boss_spawned = False
        self.player_pos = (1, 1)
        self.player_previous_tile = self.map_data[self.player_pos[0]][self.player_pos[1]]

        self.create_frame()
        self.fill_default()
        self.generate_biomes_and_patches()
        self.generate_rivers()
        self.place_structures_optimized()


    @classmethod
    def generate_map_with_seed(cls, width: int, height: int, seed: int):
        """Generates a map with a specific seed value."""
        return cls(width, height, seed)
    
    def draw(self, screen):
        """Draws the map on the given screen."""
        for x in range(self.height):
            for y in range(self.width):
                tile = self.map_data[x][y]
                if tile.image:
                    # Draw each tile image on the screen
                    self.screen.blit(tile.image, (y * self.TILE_SIZE, x * self.TILE_SIZE))
        
        # Draw enemies
        for enemy in self.enemies:
            if enemy.image:
                self.screen.blit(enemy.image, (enemy.pos[1] * self.TILE_SIZE, enemy.pos[0] * self.TILE_SIZE))

    def reset_map(self, seed):
        """Resets the map with the provided seed without reinitializing the object."""
        print(f"Resetting map with seed {seed}...")
        random.seed(seed)

        # Clear existing map data
        self.map_data = [[default for _ in range(self.width)] for _ in range(self.height)]
        self.enemies = []
        self.boss_spawned = False
        self.player_pos = (1, 1)
        self.player_previous_tile = self.map_data[self.player_pos[0]][self.player_pos[1]]

        # Regenerate map structures, biomes, rivers, and other elements
        self.create_frame()
        self.fill_default()
        self.generate_biomes_and_patches()
        self.generate_rivers()
        self.place_structures_optimized()

    def place_player(self, hero=None):
        """Places the player on the map, making sure only one instance exists."""
        if hero is None:
            x, y = self.player_pos
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
        for x in range(self.width):
            self.map_data[0][x] = self.map_data[self.height - 1][x] = Tile("=", "=", "grey", walkable=False)
        for y in range(self.height):
            self.map_data[y][0] = self.map_data[y][self.width - 1] = Tile("=", "=", "grey", walkable=False)

    def fill_default(self):
        """Fills the internal part of the map with default tiles."""
        for x in range(1, self.height - 1):
            for y in range(1, self.width - 1):
                self.map_data[x][y] = default

    def generate_biomes_and_patches(self):
        """Generates biome patches in large blocks to reduce redundant random calls."""
        biome_types = [
            (plains, 40, 10, 20),   # Increased patch count and size
            (forest, 30, 8, 15),
            (mountain, 20, 6, 12),
            (lake, 15, 6, 10),
            (brush, 20, 5, 12),
            (desert, 15, 5, 12),
            (swamp, 10, 5, 10),
            (snow, 10, 5, 10),
            (hill, 15, 5, 12)
        ]
        for tile, num_patches, min_size, max_size in biome_types:
            self.generate_patch_optimized(tile, num_patches, min_size, max_size)

    def generate_patch_optimized(self, tile, num_patches, min_size, max_size):
        """Generates patches with optimized approach."""
        for _ in range(num_patches):
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            patch_size = random.randint(min_size, max_size)
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            for _ in range(patch_size):
                dx, dy = random.choice(directions)
                x, y = min(max(1, x + dx), self.height - 2), min(max(1, y + dy), self.width - 2)
                if self.map_data[x][y] == default:
                    self.map_data[x][y] = tile

    def generate_rivers(self, num_rivers=3):
        """Generates rivers using an optimized approach."""
        for _ in range(num_rivers):
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            while self.map_data[x][y] != mountain:
                x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            length = random.randint(10, 20)
            for _ in range(length):
                self.map_data[x][y] = river
                dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                x, y = min(max(1, x + dx), self.height - 2), min(max(1, y + dy), self.width - 2)

    def place_structures_optimized(self):
        """Places structures with reduced random retries."""
        structure_params = [
            (village, default, 2, "Village"),
            (cave, mountain, 3, "Cave"),
            (ruins, plains, 2, "Ruins"),
            (shrine_tile, plains, 1, "Shrine"),
            (treasure, forest, 3, "Treasure"),
        ]
        for tile, target_tile, count, name in structure_params:
            self.place_structure(tile, target_tile, count, name)

    def place_structure(self, structure_tile, target_tile_type, count, name):
        """Optimized structure placement with limited attempts."""
        placed_count = 0
        attempts = 0
        max_attempts = 100
        while placed_count < count and attempts < max_attempts:
            x, y = random.randint(1, self.height - 2), random.randint(1, self.width - 2)
            if self.map_data[x][y] == target_tile_type:
                self.map_data[x][y] = structure_tile
                placed_count += 1
                print(f"{name} {placed_count} placed at ({x}, {y}) after {attempts + 1} attempts.")
            attempts += 1
        if placed_count < count:
            print(f"Failed to place all {name}s after {max_attempts} attempts.")

    def update_player_position(self, old_x, old_y, new_x, new_y):
        """Updates the player's position on the map."""
        self.map_data[old_x, old_y] = self.player_previous_tile
        self.player_previous_tile = self.map_data[new_x, new_y]
        self.map_data[new_x, new_y] = player
        self.player_pos = (new_x, new_y)

    def display_map(self):
        """Displays the map visually using Pygame."""
        self.screen.fill((0, 0, 0))  # Clear the screen with black

        # Calculate map pixel dimensions
        map_pixel_width = self.width * self.TILE_SIZE
        map_pixel_height = self.height * self.TILE_SIZE

        # Draw each tile on the map
        for row_idx, row in enumerate(self.map_data):
            for col_idx, tile in enumerate(row):
                if tile.image:
                    # Draw the tile image
                    self.screen.blit(tile.image, (col_idx * self.TILE_SIZE, row_idx * self.TILE_SIZE))

        # Draw each enemy on top of the map
        for enemy in self.enemies:
            if enemy.image:
                x, y = enemy.pos
                self.screen.blit(enemy.image, (y * self.TILE_SIZE, x * self.TILE_SIZE))

        # Draw the player on the map on top of everything else
        player_tile = self.map_data[self.player_pos[0]][self.player_pos[1]]
        if player_tile.image:
            self.screen.blit(player.image, (self.player_pos[1] * self.TILE_SIZE, self.player_pos[0] * self.TILE_SIZE))

        # Draw grid lines only within the map bounds
        for x in range(0, map_pixel_width, self.TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, map_pixel_height), 1)  # Vertical lines
        for y in range(0, map_pixel_height, self.TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (map_pixel_width, y), 1)  # Horizontal lines

    def enclose_map(self):
        """Enclose the map with non-walkable boundary tiles."""
        for x in range(self.width):
            self.map_data[0][x] = Tile("X", ansi_colors['gray'], walkable=False)  # Top boundary
            self.map_data[self.height - 1][x] = Tile("X", ansi_colors['gray'], walkable=False)  # Bottom boundary
        for y in range(self.height):
            self.map_data[y][0] = Tile("X", ansi_colors['gray'], walkable=False)  # Left boundary
            self.map_data[y][self.width - 1] = Tile("X", ansi_colors['gray'], walkable=False)  # Right boundary

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
        for _ in range(5):
            enemy = generate_enemy("low", cycle)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)
        for _ in range(3):
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

    def is_tile_empty(self, x, y):
        """Check if a tile is empty and suitable for enemy placement."""
        tile = self.map_data[x][y]
        # A tile is empty if it's walkable and not occupied by 'E' or 'P'
        return tile.walkable and tile.symbol_raw not in ['P'] and tile.enemy is None

    def count_available_tiles(self):
        """Counts the number of available tiles for enemy placement."""
        count = 0
        for x in range(1, self.height - 1):
            for y in range(1, self.width - 1):
                if self.is_tile_empty(x, y):
                    count += 1
        return count
    
    def calculate_map_density(self):
        """Calculates the number of walkable and occupied tiles."""
        walkable_tiles = 0
        occupied_tiles = 0
        for row in self.map_data:
            for tile in row:
                if tile.walkable:
                    walkable_tiles += 1
                    # Count the number of occupied tiles (by structures or enemies)
                    if tile.enemy or tile == village or tile == cave or tile == ruins:
                        occupied_tiles += 1

    def place_enemies_on_map(self, enemies_list):
        """Places enemies on the map."""

        for idx, enemy in enumerate(enemies_list):
            placed = False
            attempts = 0

            while not placed:
                x = random.randint(1, self.height - 2)
                y = random.randint(1, self.width - 2)
                attempts += 1

                # Check if the tile is suitable for placing an enemy
                if self.is_tile_empty(x, y):
                    # Place enemy on the tile
                    enemy.pos = (x, y)
                    enemy.underlying_tile = self.map_data[x][y]  # Store the underlying tile
                    self.enemies.append(enemy)
                    placed = True
                elif attempts > 200:  # Fail-safe after 200 attempts
                    break


    def place_boss(self):
        """Places the boss on the map after other structures and enemies are placed."""
        attempts = 0
        max_attempts = 100
        while attempts < max_attempts:
            x = random.randint(1, self.height - 2)
            y = random.randint(1, self.width - 2)

            # Check that the boss tile is a walkable tile and not overlapping with other encounters or structures
            if self.is_tile_empty(x, y) and self.map_data[x][y].walkable:
                self.map_data[x][y] = boss_tile
                print(f"Boss placed at ({x}, {y}) after {attempts + 1} attempts.")
                return (x, y)
            attempts += 1

        print(f"Failed to place Boss after {max_attempts} attempts.")

    def swap_for_shrine(self, x, y):
        """Swaps the defeated boss tile with a shrine tile."""
        self.map_data[x][y] = shrine_tile
        print(f"Shrine placed at ({x}, {y}) after boss defeated.")