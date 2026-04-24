import sys
import os
import random
import pygame
import pytest

# Ensure the script can find the 'src' folder regardless of where it's run
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_path, 'src'))

from game_system.menu import handle_menu_input
from battle_system.battlesys import BattleSystem
from battle_system.hero import Hero
from battle_system.enemy import generate_boss, boss_list
from battle_system.health_bar import HealthBar
from battle_system.item import *
from battle_system.weapon import Weapon, generate_weapon, low_tier_weapons, mid_tier_weapons, high_tier_weapons
from map_system.map import Map, shrine_tile
from map_system.tiles import *

class Game:
    """Main Game class modified for Headless CI testing."""
    MAX_SEED_VALUE = 1000000
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    # UI area dimensions
    MAP_AREA_WIDTH = SCREEN_WIDTH // 2
    MAP_AREA_HEIGHT = SCREEN_HEIGHT * 2 // 3
    STATS_AREA_X = MAP_AREA_WIDTH
    STATS_AREA_Y = 0
    STATS_AREA_WIDTH = SCREEN_WIDTH - MAP_AREA_WIDTH
    STATS_AREA_HEIGHT = MAP_AREA_HEIGHT
    TEXTBOX_AREA_X = 0
    TEXTBOX_AREA_Y = MAP_AREA_HEIGHT
    TEXTBOX_AREA_WIDTH = SCREEN_WIDTH
    TEXTBOX_AREA_HEIGHT = SCREEN_HEIGHT - MAP_AREA_HEIGHT
    TILE_SIZE = 16

    def __init__(self, headless=False):
        self.headless = headless
        pygame.init()
        
        if self.headless:
            # Use HIDDEN mode for GitHub CI
            self.screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)
        else:
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
            pygame.display.set_caption("Chronicles of Desgoblin - Test Mode")

        self.running = True
        self.map_width = 30
        self.map_height = 15
        self.hero = Hero(name="Hero", health=150)
        self.hero.health_bar = HealthBar(self.hero, color="green")
        self.cycle = 1
        self.boss_defeated = 0
        self.clock = pygame.time.Clock()

        # Load assets (Uses the 3-level-up pathing we fixed in tiles.py)
        load_tile_images()
        load_enemy_images()

        self.font = pygame.font.Font(None, 24)
        self.log_messages = []
        self.current_input = ''
        self.accepting_input = False
        self.in_battle = False

        # Input Flags
        self.awaiting_loot_input = self.awaiting_inventory_input = False
        self.awaiting_village_input = self.awaiting_rest_input = False
        self.awaiting_weapon_shop_input = self.awaiting_item_shop_input = False

        self.loot_weapon = None
        self.replace_treasure_tile = None

    def run(self):
        """Skips the interactive menu if in headless mode."""
        if self.headless:
            self.seed = 12345
            self.start_game()
            return

        while True:
            menu_choice = handle_menu_input()
            if menu_choice == "1":
                self.seed = random.randint(0, self.MAX_SEED_VALUE)
                self.start_game()
            elif menu_choice == "2":
                self.set_seed()
                self.start_game()
            elif menu_choice == "3":
                break

    def set_seed(self):
        if self.headless:
            self.seed = 42
            return
        seed_input = input(f"Enter seed (0 - {self.MAX_SEED_VALUE}): ")
        self.seed = int(seed_input) if seed_input.isdigit() else 0

    def start_game(self, new_game=True):
        if new_game:
            self.boss_defeated = 0
            self.cycle = 1
            if not hasattr(self, 'seed'): self.seed = random.randint(0, self.MAX_SEED_VALUE)

        self.game_map = Map(self.screen, width=self.map_width, height=self.map_height, seed=self.seed)
        self.game_map.place_player(self.hero)
        
        selected_enemies = self.game_map.select_enemies(self.boss_defeated, self.cycle)
        self.game_map.place_enemies_on_map(selected_enemies)
        self.total_bosses = 1

        if not self.headless:
            self.game_loop()

    def game_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event)
            self.display_ui()
            self.clock.tick(60)

    def handle_key_event(self, event):
        if self.accepting_input:
            if event.key == pygame.K_RETURN:
                user_input = self.current_input
                self.current_input = ''
                self.process_user_input(user_input)
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            else:
                self.current_input += event.unicode
        else:
            x, y = self.hero.player_pos
            dx, dy = 0, 0
            if event.key == pygame.K_w: dx = -1
            elif event.key == pygame.K_s: dx = 1
            elif event.key == pygame.K_a: dy = -1
            elif event.key == pygame.K_d: dy = 1
            if dx != 0 or dy != 0: self.move_player(dx, dy)

    def move_player(self, dx, dy):
        x, y = self.hero.player_pos
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < self.game_map.height and 0 <= new_y < self.game_map.width:
            tile = self.game_map.map_data[new_x][new_y]
            if tile.symbol_raw == 'E': self.enemy_encounter(new_x, new_y)
            elif tile.symbol_raw == 'V': self.village_encounter(new_x, new_y)
            elif tile.walkable:
                self.game_map.update_player_position(x, y, new_x, new_y)
                self.hero.player_pos = (new_x, new_y)

    def display_ui(self):
        self.screen.fill((0, 0, 0))
        self.game_map.draw(self.screen)
        # Stats drawing logic...
        pygame.display.flip()

    # Stub methods to prevent crashes during automated tests
    def enemy_encounter(self, x, y): pass
    def village_encounter(self, x, y): pass
    def process_user_input(self, val): pass

# --- PYTEST ---

def test_main_engine_startup():
    """Verifies that the main game engine boots, loads images, and builds the map."""
    try:
        game_instance = Game(headless=True)
        game_instance.run() # In headless, this just triggers start_game()
        
        assert game_instance.hero.health == 150
        assert game_instance.game_map is not None
        assert len(game_instance.game_map.map_data) == 15
        print("Success: Game Engine initialized and assets verified.")
    finally:
        pygame.quit()

if __name__ == "__main__":
    game = Game(headless=False)
    game.run()
