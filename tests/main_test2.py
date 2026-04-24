import sys
import os
import random
import pygame

# Adding paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
    """Main Game class to manage game flow and state."""
    MAX_SEED_VALUE = 1000000  # Maximum integer value allowed for seed
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    # UI area dimensions
    MAP_AREA_WIDTH = SCREEN_WIDTH // 2  # Left half for map
    MAP_AREA_HEIGHT = SCREEN_HEIGHT * 2 // 3  # Top two-thirds for map

    STATS_AREA_X = MAP_AREA_WIDTH
    STATS_AREA_Y = 0
    STATS_AREA_WIDTH = SCREEN_WIDTH - MAP_AREA_WIDTH
    STATS_AREA_HEIGHT = MAP_AREA_HEIGHT

    TEXTBOX_AREA_X = 0
    TEXTBOX_AREA_Y = MAP_AREA_HEIGHT
    TEXTBOX_AREA_WIDTH = SCREEN_WIDTH
    TEXTBOX_AREA_HEIGHT = SCREEN_HEIGHT - MAP_AREA_HEIGHT

    TILE_SIZE = 16  # Adjusted tile size for better visibility

    def __init__(self, screen=None):
        if screen is None:
            pygame.init()
            self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        else:
            self.screen = screen

        self.running = True
        self.map_width = 30
        self.map_height = 15

        self.hero = Hero(name="Hero", health=150)
        self.hero.health_bar = HealthBar(self.hero, color="green")
        self.cycle = 1
        self.boss_defeated = 0
        self.game_over_count = {}

        pygame.init()
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Chronicles of Desgoblin")
        self.clock = pygame.time.Clock()

        # Load assets
        load_tile_images()
        load_enemy_images()

        self.font = pygame.font.Font(None, 24)
        self.log_messages = []
        self.current_input = ''
        self.accepting_input = False
        self.in_battle = False

        # Initialize flags for different inputs
        self.awaiting_loot_input = False
        self.awaiting_inventory_input = False
        self.awaiting_village_input = False
        self.awaiting_rest_input = False
        self.awaiting_weapon_shop_input = False
        self.awaiting_item_shop_input = False

        # For treasure encounters
        self.loot_weapon = None
        self.replace_treasure_tile = None

    def run(self) -> None:
        """Runs the main game loop, offering options for new game or seed-based game."""
        while True:
            # Handle menu input
            menu_choice = handle_menu_input()
            if menu_choice == "1":  # New game
                self.seed = random.randint(0, self.MAX_SEED_VALUE)
                self.start_game()
            elif menu_choice == "2":  # Options -> Set Seed Game
                self.set_seed()
                self.start_game()
            elif menu_choice == "3":  # Exit
                break

    def set_seed(self):
        """Sets a seed value for the map, with validation for the seed range."""
        while True:
            try:
                seed_input = int(input(f"Enter seed (0 - {self.MAX_SEED_VALUE}): "))
                if 0 <= seed_input <= self.MAX_SEED_VALUE:
                    self.seed = seed_input
                    break
                else:
                    print(f"Please enter a value between 0 and {self.MAX_SEED_VALUE}.")
            except ValueError:
                print("Invalid input. Please enter an integer.")

    def start_game(self, new_game=True):
        """Starts a new game or level, resetting the map with a seed instead of reinitializing it."""
        if new_game:
            self.hero = Hero(name="Hero", health=150)
            self.hero.health_bar = HealthBar(self.hero, color="green")
            self.boss_defeated = 0
            self.cycle = 1
            self.seed = random.randint(0, self.MAX_SEED_VALUE)

        # Initialize or reset the map
        self.game_map = Map(self.screen, width=self.map_width, height=self.map_height, seed=self.seed)
        self.game_map.place_player(self.hero)

        # Select and place enemies
        selected_enemies = self.game_map.select_enemies(self.boss_defeated, self.cycle)
        self.game_map.place_enemies_on_map(selected_enemies)

        self.total_bosses = 1  # Total bosses to defeat

        # Main game loop
        self.game_loop()

    def game_loop(self):
        """Main game loop using Pygame."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("Quit event received.")
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_key_event(event)

            self.display_ui()
            self.clock.tick(60)  # Limit to 60 FPS

            # Check if boss is defeated
            if self.boss_defeated >= self.total_bosses:
                self.display_final_victory_screen()
                break

    def handle_key_event(self, event):
        """Handles key events for player movement and actions."""
        if self.accepting_input:
            if event.key == pygame.K_RETURN:
                user_input = self.current_input
                self.current_input = ''
                if self.in_battle:
                    self.process_battle_input(user_input)
                else:
                    self.process_user_input(user_input)
            elif event.key == pygame.K_BACKSPACE:
                self.current_input = self.current_input[:-1]
            else:
                self.current_input += event.unicode
        else:
            x, y = self.hero.player_pos
            new_x, new_y = x, y

            if event.key == pygame.K_w:
                new_x = max(0, x - 1)
            elif event.key == pygame.K_s:
                new_x = min(self.game_map.height - 1, x + 1)
            elif event.key == pygame.K_a:
                new_y = max(0, y - 1)
            elif event.key == pygame.K_d:
                new_y = min(self.game_map.width - 1, y + 1)
            elif event.key == pygame.K_i:
                self.access_inventory()
                return
            elif event.key == pygame.K_q:
                print("Quitting game...")
                self.running = False
                pygame.quit()
                sys.exit()
            else:
                return  # Ignore other keys

            self.move_player(new_x - x, new_y - y)

    def move_player(self, dx, dy):
        """Moves the player and handles encounters."""
        x, y = self.hero.player_pos
        new_x, new_y = x + dx, y + dy

        # Validate movement within map bounds
        if new_x < 0 or new_x >= self.game_map.height or new_y < 0 or new_y >= self.game_map.width:
            self.log_messages.append("Invalid move. Stay within bounds.")
            return

        # Get the tile at the new position
        tile = self.game_map.map_data[new_x][new_y]
        tile_symbol = tile.symbol_raw

        # Modular encounter system using a dictionary of encounters
        encounter_handlers = {
            'E': lambda: self.enemy_encounter(new_x, new_y),
            'S': lambda: self.shrine_encounter(new_x, new_y),
            '~': lambda: self.invalid_move(),
            '#': lambda: self.invalid_move(),
            'N': lambda: self.npc_encounter(new_x, new_y),
            'V': lambda: self.village_encounter(new_x, new_y),
            'T': lambda: self.treasure_encounter(new_x, new_y),
        }

        if tile_symbol in encounter_handlers:
            encounter_handlers[tile_symbol]()
        else:
            # Move the player
            self.game_map.update_player_position(x, y, new_x, new_y)
            self.hero.player_pos = (new_x, new_y)

    def access_inventory(self):
        """Allows the player to view and use items from their inventory."""
        self.log_messages.append("Inventory:")
        for idx, item in enumerate(self.hero.items, 1):
            self.log_messages.append(f"{idx}. {item.name} - {item.description}")
        self.log_messages.append("Type the number of the item to use it, or 'b' to go back.")
        self.accepting_input = True
        self.awaiting_inventory_input = True

    def process_user_input(self, user_input):
        """Processes user input when not in battle."""
        if self.awaiting_loot_input:
            self.handle_loot_input(user_input)
        elif self.awaiting_inventory_input:
            self.handle_inventory_input(user_input)
        elif self.awaiting_village_input:
            self.handle_village_input(user_input)
        elif self.awaiting_rest_input:
            self.handle_rest_input(user_input)
        elif self.awaiting_weapon_shop_input:
            self.handle_weapon_shop_input(user_input)
        elif self.awaiting_item_shop_input:
            self.handle_item_shop_input(user_input)
        else:
            self.log_messages.append("No action to process.")
            self.accepting_input = False

    def handle_loot_input(self, user_input):
        if user_input.lower() == 'p':
            self.log_messages.append(f"You picked up {self.loot_weapon.name}.")
            self.hero.equip_weapon(self.loot_weapon)
        elif user_input.lower() == 's':
            self.log_messages.append(f"Scrapped {self.loot_weapon.name} for {self.loot_weapon.value} gold.")
            self.hero.cashpile += self.loot_weapon.value
            self.log_messages.append(f"Your cashpile now contains {self.hero.cashpile} gold.")
        else:
            self.log_messages.append("Invalid input. Please enter 'p' or 's'.")
            return

        self.loot_weapon = None
        self.accepting_input = False
        self.awaiting_loot_input = False

        # Replace the treasure tile after the player decision
        if self.replace_treasure_tile:
            x, y = self.replace_treasure_tile
            self.game_map.map_data[x][y] = treasure_empty
            self.replace_treasure_tile = None

    def handle_inventory_input(self, user_input):
        if user_input.lower() == 'b':
            self.accepting_input = False
            self.awaiting_inventory_input = False
        elif user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(self.hero.items):
                item = self.hero.items.pop(idx)
                self.log_messages.append(f"You used {item.name}.")
                item.use(self.hero)
            else:
                self.log_messages.append("Invalid item number.")
        else:
            self.log_messages.append("Invalid input.")

    def enemy_encounter(self, x, y):
        """Handles encounters with enemies."""
        enemy = self.game_map.map_data[x][y].enemy
        if enemy:
            self.log_messages.append(f"Enemy encountered: {enemy.name}")
            self.battle_loop(enemy)
            if not self.hero.alive:
                self.handle_game_over()
                return
            if not enemy.alive:
                self.log_messages.append(f"You have defeated the {enemy.name}!")
                self.game_map.map_data[x][y].enemy = None
                self.game_map.enemies.remove(enemy)
                self.handle_loot(enemy)
                self.game_map.update_player_position(self.hero.player_pos[0], self.hero.player_pos[1], x, y)
                self.hero.player_pos = (x, y)
        else:
            self.log_messages.append("Error: Enemy not found at this position.")

    def handle_loot(self, enemy):
        """Handles looting after defeating an enemy."""
        item = self.enemy_drop_item(enemy)
        if item:
            self.log_messages.append(f"The enemy dropped {item.name}!")
            self.hero.items.append(item)
        else:
            self.log_messages.append("The enemy did not drop any items.")

        self.log_messages.append(f"You found {enemy.weapon.name} (Tier: {enemy.tier.capitalize()}) (Damage: {enemy.weapon.damage}). Value: {enemy.weapon.value} gold.")
        self.log_messages.append("Do you want to pick it up or scrap it for gold? (p/s)")
        self.accepting_input = True
        self.awaiting_loot_input = True
        self.loot_weapon = enemy.weapon

    def shrine_encounter(self, x, y):
        """Handles the shrine encounter leading to a boss battle."""
        self.log_messages.append("You have discovered the shrine!")
        boss = generate_boss(self.boss_defeated % len(boss_list))
        self.battle_loop(boss)

        if not self.hero.alive:
            self.handle_game_over()
            return
        if not boss.alive:
            self.log_messages.append(f"You have defeated {boss.name}!")
            for item_name in boss.drops:
                item = create_item_from_name(item_name)
                self.hero.items.append(item)
                self.log_messages.append(f"You received {item.name}!")
            self.boss_defeated += 1
            self.display_level_up_message()
            self.start_new_level()

    def treasure_encounter(self, x, y):
        """Handles encounters with treasures."""
        self.log_messages.append("You found a treasure chest!")
        weapon_tier = None
        random_roll = random.randint(1, 100)
        if random_roll <= 60:
            weapon_tier = "low"
        elif random_roll <= 90:
            weapon_tier = "mid"
        else:
            weapon_tier = "high"

        if weapon_tier:
            weapon = generate_weapon(weapon_tier)
            self.log_messages.append(f"You found a {weapon.name} (Tier: {weapon_tier.capitalize()})!")
            self.log_messages.append("Do you want to pick it up or scrap it for gold? (p/s)")
            self.accepting_input = True
            self.awaiting_loot_input = True
            self.loot_weapon = weapon
            self.replace_treasure_tile = (x, y)
        else:
            self.log_messages.append("You found no valuable weapons.")
            self.game_map.map_data[x][y] = treasure_empty

        self.game_map.update_player_position(self.hero.player_pos[0], self.hero.player_pos[1], x, y)
        self.hero.player_pos = (x, y)

    def village_encounter(self, x, y):
        """Handles encounters with villages."""
        self.log_messages.append("You enter a village.")
        self.village_menu()
        self.game_map.update_player_position(self.hero.player_pos[0], self.hero.player_pos[1], x, y)
        self.hero.player_pos = (x, y)

    def village_menu(self):
        """Displays the village menu and handles interactions."""
        self.log_messages.append("Welcome to the village!")
        self.log_messages.append("1. Rest")
        self.log_messages.append("2. Visit Weapon Shop")
        self.log_messages.append("3. Visit Item Shop")
        self.log_messages.append("4. Leave Village")
        self.accepting_input = True
        self.awaiting_village_input = True

    def handle_village_input(self, user_input):
        if user_input == '1':
            self.rest_menu()
        elif user_input == '2':
            self.weapon_shop()
        elif user_input == '3':
            self.item_shop()
        elif user_input == '4':
            self.log_messages.append("Leaving the village.")
            self.accepting_input = False
            self.awaiting_village_input = False
        else:
            self.log_messages.append("Invalid choice. Try again.")

    def rest_menu(self):
        """Displays rest options in the village."""
        self.log_messages.append("Resting Options:")
        self.log_messages.append("1. Stanza Lercia (30% HP for 15 gold)")
        self.log_messages.append("2. Stanza (50% HP for 25 gold)")
        self.log_messages.append("3. Stanza Pregio (100% HP for 35 gold)")
        self.accepting_input = True
        self.awaiting_rest_input = True

    def handle_rest_input(self, user_input):
        if user_input == '1' and self.hero.cashpile >= 15:
            heal_amount = int(self.hero.health_max * 0.3)
            self.hero.health = min(self.hero.health + heal_amount, self.hero.health_max)
            self.hero.cashpile -= 15
            self.log_messages.append("You rested badly in a Stanza Lercia and healed 30% of your HP.")
        elif user_input == '2' and self.hero.cashpile >= 25:
            heal_amount = int(self.hero.health_max * 0.5)
            self.hero.health = min(self.hero.health + heal_amount, self.hero.health_max)
            self.hero.cashpile -= 25
            self.log_messages.append("You rested in a Stanza and healed 50% of your HP.")
        elif user_input == '3' and self.hero.cashpile >= 35:
            self.hero.health = self.hero.health_max
            self.hero.cashpile -= 35
            self.log_messages.append("You rested well in a Stanza Pregio and healed completely.")
        else:
            self.log_messages.append("You don't have enough gold for this option.")
        self.accepting_input = False
        self.awaiting_rest_input = False

    def weapon_shop(self):
        """Handles the weapon shop interactions."""
        self.log_messages.append("Welcome to the Weapon Shop!")
        self.weapons_for_sale = (
            [generate_weapon("low") for _ in range(5)] +
            [generate_weapon("mid") for _ in range(4)] +
            [generate_weapon("high") for _ in range(2)]
        )
        for idx, weapon in enumerate(self.weapons_for_sale, 1):
            self.log_messages.append(f"{idx}. {weapon.name} (Tier: {weapon.tier.capitalize()}) - Damage: {weapon.damage} - {weapon.value} gold")
        self.log_messages.append("Select a weapon to buy or 'b' to go back:")
        self.accepting_input = True
        self.awaiting_weapon_shop_input = True

    def handle_weapon_shop_input(self, user_input):
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(self.weapons_for_sale):
                weapon = self.weapons_for_sale[idx]
                if self.hero.cashpile >= weapon.value:
                    self.hero.cashpile -= weapon.value
                    self.hero.equip_weapon(weapon)
                    self.log_messages.append(f"You bought and equipped {weapon.name}.")
                else:
                    self.log_messages.append("You don't have enough gold.")
            else:
                self.log_messages.append("Invalid selection.")
            self.accepting_input = False
            self.awaiting_weapon_shop_input = False
        elif user_input.lower() == 'b':
            self.accepting_input = False
            self.awaiting_weapon_shop_input = False
        else:
            self.log_messages.append("Invalid input.")

    def item_shop(self):
        """Handles the item shop interactions."""
        self.log_messages.append("Welcome to the Item Shop!")
        self.items_for_sale = [
            generate_cure("small"),
            generate_cure("mids"),
            generate_cure("midh"),
            generate_throwable("small"),
            generate_throwable("mids")
        ]
        for idx, item in enumerate(self.items_for_sale, 1):
            self.log_messages.append(f"{idx}. {item.name} - {item.description} - {item.value} gold")
        self.log_messages.append("Select an item to buy or 'b' to go back:")
        self.accepting_input = True
        self.awaiting_item_shop_input = True

    def handle_item_shop_input(self, user_input):
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(self.items_for_sale):
                item = self.items_for_sale[idx]
                if self.hero.cashpile >= item.value:
                    self.hero.cashpile -= item.value
                    self.hero.items.append(item)
                    self.log_messages.append(f"You bought {item.name}.")
                else:
                    self.log_messages.append("You don't have enough gold.")
            else:
                self.log_messages.append("Invalid selection.")
            self.accepting_input = False
            self.awaiting_item_shop_input = False
        elif user_input.lower() == 'b':
            self.accepting_input = False
            self.awaiting_item_shop_input = False
        else:
            self.log_messages.append("Invalid input.")

    def display_final_victory_screen(self):
        """Displays the final victory screen."""
        self.log_messages.append("Congratulations! You have defeated all the bosses and completed the game!")
        self.running = False

    def handle_game_over(self):
        """Handles the game-over logic."""
        self.log_messages.append("Game Over!")
        self.running = False

    def display_level_up_message(self):
        """Displays a message after defeating a boss."""
        self.log_messages.append(f"You have defeated {self.boss_defeated} out of {self.total_bosses} bosses.")
        if self.boss_defeated < self.total_bosses:
            self.log_messages.append("Prepare yourself for the next challenge!")
        else:
            self.log_messages.append("Congratulations! You have defeated all the bosses!")

    def start_new_level(self):
        """Starts a new level with increased difficulty."""
        self.cycle += 1
        self.log_messages.append(f"Starting New Game+{self.cycle}")
        self.seed = random.randint(0, self.MAX_SEED_VALUE)
        self.log_messages.append(f"Generating new map with seed: {self.seed}")
        self.start_game(new_game=False)

    def battle_loop(self, enemy):
        """Handles the battle loop."""
        self.in_battle = True
        self.accepting_input = True
        self.current_input = ''
        self.battle_log = []

        while self.in_battle:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.in_battle = False
                    self.running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.handle_battle_key_event(event)

            self.display_battle_ui(enemy)
            self.clock.tick(60)

            if self.in_battle:
                enemy_action = enemy.choose_action()
                if enemy_action == 'attack':
                    damage = enemy.attack(self.hero)
                    self.battle_log.append(f"The {enemy.name} attacks you for {damage} damage!")
                    if not self.hero.alive:
                        self.battle_log.append("You have been defeated!")
                        self.in_battle = False
                        self.accepting_input = False

    def handle_battle_key_event(self, event):
        """Handles key events during battle."""
        if event.key == pygame.K_RETURN:
            user_input = self.current_input
            self.current_input = ''
            self.process_battle_input(user_input)
        elif event.key == pygame.K_BACKSPACE:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input += event.unicode

    def process_battle_input(self, user_input):
        """Processes user input during battle."""
        action = user_input.lower()
        if action == 'attack':
            damage = self.hero.attack(enemy)
            self.battle_log.append(f"You attack the {enemy.name} for {damage} damage!")
            if not enemy.alive:
                self.battle_log.append(f"You defeated the {enemy.name}!")
                self.in_battle = False
                self.accepting_input = False
        elif action == 'defend':
            self.battle_log.append("You brace yourself for the next attack.")
        elif action == 'item':
            self.battle_log.append("You use an item.")
        elif action == 'run':
            self.battle_log.append("You attempt to run away.")
            self.in_battle = False
            self.accepting_input = False
        else:
            self.battle_log.append("Invalid action. Choose 'attack', 'defend', 'item', or 'run'.")

        if self.in_battle:
            enemy_action = self.enemy.choose_action()
            if enemy_action == 'attack':
                damage = self.enemy.attack(self.hero)
                self.battle_log.append(f"The {enemy.name} attacks you for {damage} damage!")
                if not self.hero.alive:
                    self.battle_log.append("You have been defeated!")
                    self.in_battle = False
                    self.accepting_input = False

    def display_ui(self):
        """Displays the entire UI including map, stats, and text box."""
        self.screen.fill((0, 0, 0))

        # Draw map area
        map_rect = pygame.Rect(0, 0, self.MAP_AREA_WIDTH, self.MAP_AREA_HEIGHT)
        self.game_map.draw(self.screen)

        # Draw stats area
        stats_rect = pygame.Rect(self.STATS_AREA_X, self.STATS_AREA_Y, self.STATS_AREA_WIDTH, self.STATS_AREA_HEIGHT)
        pygame.draw.rect(self.screen, (50, 50, 50), stats_rect)
        y_offset = self.STATS_AREA_Y + 10
        line_height = 24

        stats_texts = [
            f"Name: {self.hero.name}",
            f"HP: {self.hero.health}/{self.hero.health_max}",
            f"Weapon: {self.hero.weapon.name if self.hero.weapon else 'None'}",
            f"Damage: {self.hero.weapon.damage if self.hero.weapon else 'N/A'}",
            f"Cash: {self.hero.cashpile} gold",
            "Inventory:"
        ]
        for stat in stats_texts:
            stat_surface = self.font.render(stat, True, (255, 255, 255))
            self.screen.blit(stat_surface, (self.STATS_AREA_X + 10, y_offset))
            y_offset += line_height

        max_inventory_items_display = 5
        for idx, item in enumerate(self.hero.items[:max_inventory_items_display]):
            item_text = f"- {item.name}"
            item_surface = self.font.render(item_text, True, (255, 255, 255))
            self.screen.blit(item_surface, (self.STATS_AREA_X + 20, y_offset))
            y_offset += line_height

        if len(self.hero.items) > max_inventory_items_display:
            more_items_text = f"...and {len(self.hero.items) - max_inventory_items_display} more items"
            more_items_surface = self.font.render(more_items_text, True, (255, 255, 255))
            self.screen.blit(more_items_surface, (self.STATS_AREA_X + 20, y_offset))
            y_offset += line_height

        text_box_rect = pygame.Rect(self.TEXTBOX_AREA_X, self.TEXTBOX_AREA_Y, self.TEXTBOX_AREA_WIDTH, self.TEXTBOX_AREA_HEIGHT)
        pygame.draw.rect(self.screen, (100, 100, 100), text_box_rect)

        line_height = 20
        max_log_lines = int(self.TEXTBOX_AREA_HEIGHT / line_height) - 1
        log_start_index = max(0, len(self.log_messages) - max_log_lines)
        y_offset = self.TEXTBOX_AREA_Y + 5
        for log_message in self.log_messages[log_start_index:]:
            log_surface = self.font.render(log_message, True, (255, 255, 255))
            self.screen.blit(log_surface, (self.TEXTBOX_AREA_X + 5, y_offset))
            y_offset += line_height

        input_prompt = "> " + self.current_input
        input_surface = self.font.render(input_prompt, True, (255, 255, 255))
        self.screen.blit(input_surface, (self.TEXTBOX_AREA_X + 5, self.TEXTBOX_AREA_Y + self.TEXTBOX_AREA_HEIGHT - line_height - 5))

        pygame.display.flip()

    def display_battle_ui(self, enemy):
        """Displays the battle UI with sprites, health bars, and labels for the hero and enemy."""
        self.screen.fill((0, 0, 0))

        font = pygame.font.Font(None, 24)
        sprite_size = 100
        line_height = 24

        hero_x, hero_y = 50, 150
        health_bar_width = 150

        if self.hero.sprite:
            hero_sprite = pygame.transform.scale(self.hero.sprite, (sprite_size, sprite_size))
            self.screen.blit(hero_sprite, (hero_x, hero_y))

        hero_health_ratio = self.hero.health / self.hero.health_max
        hero_health_bar_rect = pygame.Rect(hero_x, hero_y - 40, int(health_bar_width * hero_health_ratio), 15)
        pygame.draw.rect(self.screen, (0, 255, 0), hero_health_bar_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(hero_x + int(health_bar_width * hero_health_ratio), hero_y - 40, int(health_bar_width * (1 - hero_health_ratio)), 15))

        hero_label = font.render("Hero", True, (255, 255, 255))
        self.screen.blit(hero_label, (hero_x, hero_y - 60))

        enemy_x, enemy_y = self.SCREEN_WIDTH - sprite_size - 50, 150

        if enemy.sprite:
            enemy_sprite = pygame.transform.scale(enemy.sprite, (sprite_size, sprite_size))
            self.screen.blit(enemy_sprite, (enemy_x, enemy_y))

        enemy_health_ratio = enemy.health / enemy.health_max
        enemy_health_bar_rect = pygame.Rect(enemy_x, enemy_y - 40, int(health_bar_width * enemy_health_ratio), 15)
        pygame.draw.rect(self.screen, (0, 255, 0), enemy_health_bar_rect)
        pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(enemy_x + int(health_bar_width * enemy_health_ratio), enemy_y - 40, int(health_bar_width * (1 - enemy_health_ratio)), 15))

        enemy_label = font.render(enemy.name, True, (255, 255, 255))
        self.screen.blit(enemy_label, (enemy_x, enemy_y - 60))

        text_box_rect = pygame.Rect(0, self.SCREEN_HEIGHT // 2, self.SCREEN_WIDTH, self.SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (100, 100, 100), text_box_rect)

        options = [
            "Battle Moves: ",
            "Attack (a)",
            "Skills (s)",
            "Item (i)",
            "Escape (e)"
        ]
        y_offset = self.SCREEN_HEIGHT // 2 + 10
        for option in options:
            option_surface = font.render(option, True, (255, 255, 255))
            self.screen.blit(option_surface, (10, y_offset))
            y_offset += line_height

        max_log_lines = 6
        log_start_index = max(0, len(self.battle_log) - max_log_lines)
        y_offset = self.SCREEN_HEIGHT // 2 + 120
        for log_message in self.battle_log[log_start_index:]:
            log_surface = font.render(log_message, True, (255, 255, 255))
            self.screen.blit(log_surface, (10, y_offset))
            y_offset += line_height

        input_prompt = "> " + self.current_input
        input_surface = font.render(input_prompt, True, (255, 255, 255))
        self.screen.blit(input_surface, (10, self.SCREEN_HEIGHT - 40))