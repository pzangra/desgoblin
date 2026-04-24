


import sys
import os
import pygame
import random as rand

from map_system.map import Map
from tiles import load_tile_images
from battle_system.enemy import generate_enemy

# Adding the root directory to the system path to access assets and other files
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MapTester:

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    TILE_SIZE = 16  # Size of each tile in pixels

    def __init__(self):
        self.running = True
        self.seed = rand.randint(0, 1000) # Use a fixed seed for reproducibility
        self.map_width = 30
        self.map_height = 20

        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Map System Test")
        self.clock = pygame.time.Clock()
        
        load_tile_images()

        # Generate the map with the specified seed to ensure consistency
        self.game_map = Map(self.screen, self.map_width, self.map_height, self.seed)
        self.hero_position = (1, 1)  # Starting position of the player
        self.game_map.place_player(None)  # Place player at the initial position

        # Generate enemies
        self.generate_and_place_enemies()

    def run(self):
        """Runs the main test loop for the map system."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event)

            # Draw the map
            self.display_map()

            # Update the display
            pygame.display.flip()
            self.clock.tick(30)  # Limit to 30 FPS for simplicity

    def generate_and_place_enemies(self):
        """Generates and places enemies on the map using the same method as main.py."""
        # Example logic for generating a list of enemies
        enemies_list = []
        level_multiplier = 1.2  # You can adjust this to match main.py settings

        for _ in range(5):
            enemy = generate_enemy("low", cycle=0)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)
        
        for _ in range(3):
            enemy = generate_enemy("mid", cycle=0)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)
        
        for _ in range(2):
            enemy = generate_enemy("high", cycle=0)
            enemy.scale_stats(level_multiplier)
            enemies_list.append(enemy)

        # Place enemies on the map
        self.game_map.place_enemies_on_map(enemies_list)  

    def handle_key_event(self, event):
        """Handles key events for player movement."""
        x, y = self.hero_position
        new_x, new_y = x, y

        # WASD controls to move the player
        if event.key == pygame.K_w:
            new_x = max(1, x - 1)
        elif event.key == pygame.K_s:
            new_x = min(self.map_height - 2, x + 1)
        elif event.key == pygame.K_a:
            new_y = max(1, y - 1)
        elif event.key == pygame.K_d:
            new_y = min(self.map_width - 2, y + 1)

        # Validate movement within map bounds
        if new_x != x or new_y != y:
            self.game_map.update_player_position(x, y, new_x, new_y)
            self.hero_position = (new_x, new_y)
            
    def display_map(self):
        """Displays the map visually using Pygame."""
        self.screen.fill((0, 0, 0))  # Clear the screen with black

        # Calculate map pixel dimensions
        map_pixel_width = self.map_width * self.TILE_SIZE
        map_pixel_height = self.map_height * self.TILE_SIZE

        # Draw each tile on the map
        for row_idx, row in enumerate(self.game_map.map_data):
            for col_idx, tile in enumerate(row):
                if tile.image:
                    # Draw the tile image
                    self.screen.blit(tile.image, (col_idx * self.TILE_SIZE, row_idx * self.TILE_SIZE))

        # Draw the player on the map
        player_tile = self.game_map.map_data[self.hero_position[0]][self.hero_position[1]]
        if player_tile.image:
            # Draw the player tile
            self.screen.blit(player_tile.image, (self.hero_position[1] * self.TILE_SIZE, self.hero_position[0] * self.TILE_SIZE))
    
        # Draw each enemy on the map
        for enemy in self.game_map.enemies:
            if enemy.image:
                x, y = enemy.pos
                self.screen.blit(enemy.image, (y * self.TILE_SIZE, x * self.TILE_SIZE))

        # Draw grid lines only within the map bounds
        for x in range(0, map_pixel_width, self.TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (x, 0), (x, map_pixel_height), 1)  # Vertical lines
        for y in range(0, map_pixel_height, self.TILE_SIZE):
            pygame.draw.line(self.screen, (0, 0, 0), (0, y), (map_pixel_width, y), 1)  # Horizontal lines


if __name__ == "__main__":
    tester = MapTester()
    tester.run()
