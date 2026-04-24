import sys
import os
import pygame
import random as rand
import pytest

from map_system.map import Map
from map_system.tiles import load_tile_images
from battle_system.enemy import generate_enemy

class MapTester:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    TILE_SIZE = 16 

    def __init__(self, headless=False):
        self.running = True
        self.seed = rand.randint(0, 1000)
        self.map_width = 30
        self.map_height = 20

        # 1. INITIALIZE PYGAME
        pygame.init()
        
        if headless:
            # Create a hidden surface for CI (no window pops up)
            self.screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("Map System Test")
        
        self.clock = pygame.time.Clock()

        # 2. LOAD ASSETS
        load_tile_images()

        # 3. GENERATE MAP
        self.game_map = Map(self.screen, self.map_width, self.map_height, self.seed)
        self.hero_position = (1, 1)
        self.game_map.place_player(None)

        self.generate_and_place_enemies()

    def generate_and_place_enemies(self):
        enemies_list = []
        level_multiplier = 1.2
        for tier, count in [("low", 5), ("mid", 3), ("high", 2)]:
            for _ in range(count):
                enemy = generate_enemy(tier, cycle=0)
                enemy.scale_stats(level_multiplier)
                enemies_list.append(enemy)
        self.game_map.place_enemies_on_map(enemies_list)

    def run(self):
        """Standard loop for manual testing."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.display_map()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()

    def display_map(self):
        self.screen.fill((0, 0, 0))
        for row_idx, row in enumerate(self.game_map.map_data):
            for col_idx, tile in enumerate(row):
                if tile.image:
                    self.screen.blit(tile.image, (col_idx * self.TILE_SIZE, row_idx * self.TILE_SIZE))
        # (Rest of your drawing logic remains here...)

# --- PYTEST INTEGRATION ---

def test_map_system_load():
    """
    This function is what GitHub Actions will run. 
    It ensures the map generates and assets load without crashing.
    """
    try:
        tester = MapTester(headless=True)
        
        # Assertions: Check if the map was actually built
        assert tester.game_map is not None
        assert len(tester.game_map.map_data) == tester.map_height
        assert len(tester.game_map.enemies) > 0
        
        print("CI Check: Map system initialized and assets loaded successfully.")
    finally:
        pygame.quit()

if __name__ == "__main__":
    # If you run this file manually, it opens the window and runs the loop
    tester = MapTester(headless=False)
    tester.run()
