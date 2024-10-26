# game_system/main.py

import sys
import os
import time
import keyboard
import random as rand

# Adding paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from map_system.map import Map
from game_system.menu import handle_menu_input
from battle_system.battlesys import BattleSystem
from battle_system.character import Hero
from battle_system.enemy import generate_boss, boss_list
from battle_system.health_bar import HealthBar
from battle_system.item import *
from battle_system.weapon import Weapon,generate_weapon, low_tier_weapons, mid_tier_weapons, high_tier_weapons
from map_system.map import shrine

class Game:
    """Main Game class to manage game flow and state."""
    MAX_SEED_VALUE = 1000000 # Maximum integer value allowed for seed

    def __init__(self):
        self.running = True
        self.hero = Hero(name="Hero", health=150)
        self.hero.health_bar = HealthBar(self.hero, color="green")
        self.current_village_tile = None  # For village interaction
        self.cycle = 0 #initializes game cycle
        self.boss_defeated = 0  #counts boss defeated, initializes
        self.game_over_count = {}  # Dictionary to track retries for each seed

    def clear(self) -> None:
        """Clears the console screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def run(self) -> None:
        """Runs the main game loop, offering options for new game or seed-based game."""
        while True:
            self.clear()
            menu_choice = handle_menu_input()

            if menu_choice == "1":  # New game
                self.seed = rand.randint(0, self.MAX_SEED_VALUE)
                self.start_game()
            elif menu_choice == "2":  # Options -> Set Seed Game
                self.set_seed()
                self.start_game()
            elif menu_choice == "3":  # Exit (handled in handle_menu_input())
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
        """Starts a new game or level, initializing the map with a seed."""
        if new_game:
            self.hero = Hero(name="Hero", health=150)
            self.hero.health_bar = HealthBar(self.hero, color="green")
            self.boss_defeated = 0  # Reset boss count for a new game
            self.cycle += 1 #increase cycle count for newgamecycle
        print(f"Using seed: {self.seed}")
        print("Initializing map...")

        # Create the map using the given seed
        map_w, map_h = 35, 25
        game_map = Map.generate_map_with_seed(map_w, map_h, self.seed)
        print("Map initialized")
        game_map.place_player(self.hero)
        print("Player placed")

        # Select and place enemies
        selected_enemies = game_map.select_enemies(self.boss_defeated, self.cycle)
        print(f"{len(selected_enemies)} enemies selected")
        game_map.place_enemies_on_map(selected_enemies)
        print("Enemies placed on map")

        
        self.total_bosses = 10  # Total bosses to defeat

        # Main game loop
        while self.running:
            self.clear()
            game_map.display_map(self.hero)  # Display the map
            self.move_player(game_map)  # Handle player movement
            if not game_map.enemies and not game_map.boss_spawned:
                self.spawn_shrine(game_map)

            # Check if boss is defeated
            if self.boss_defeated >= self.total_bosses:
                self.display_final_victory_screen()
                break

        print("Game Over. Thanks for playing!")

    def handle_game_over(self) -> None:
        """Handles the game-over logic, allowing retries with the same or different seed."""
        if self.seed not in self.game_over_count:
            self.game_over_count[self.seed] = 0
        self.game_over_count[self.seed] += 1

        retry_allowed = self.game_over_count[self.seed] <= 5

        # Game over screen
        self.clear()
        print("Game Over!")
        print(f"You have died {self.game_over_count[self.seed]} times on this seed.")
        if self.game_over_count[self.seed] > 5:
            print("Retry limit exceeded for this seed. You must select a new seed.")

        # Ask for retry or new seed
        while True:
            if retry_allowed:
                choice = input("Would you like to retry with the same seed (r) or enter a new one (n)? ").lower()
            else:
                choice = input("Please enter a new seed (n): ").lower()

            if choice == 'r' and retry_allowed:
                # Retry with the same seed
                self.running = True
                break
            elif choice == 'n':
                # Set a new seed
                self.set_seed()
                self.running = True
                break
            else:
                print("Invalid input. Please try again.")

    def display_victory_screen(self):
        """Displays the victory screen."""
        self.clear()
        print("Congratulations! You defeated all enemies.")
        input("Press Enter to exit...")
        self.running = False

    def move_player(self, game_map: Map):
        """Handles player movement and interactions on the map in real-time."""

        x, y = self.hero.player_pos  # Use hero's position to determine starting point
        print("Use W/A/S/D to move the player, 'I' to access inventory. Press Q to quit.")

        while True:
            new_x, new_y = x, y

            # Wait for a key event from the user
            key_event = keyboard.read_event(suppress=True)

            if key_event.event_type == keyboard.KEY_DOWN:
                key = key_event.name.lower()

                # Determine new position based on input
                if key == 'w':
                    new_x, new_y = x - 1, y
                elif key == 's':
                    new_x, new_y = x + 1, y
                elif key == 'a':
                    new_x, new_y = x, y - 1
                elif key == 'd':
                    new_x, new_y = x, y + 1
                elif key == 'i':
                    self.access_inventory()
                    self.clear()
                    game_map.display_map(self.hero)
                    continue
                elif key == 'q':
                    print("Quitting game...")
                    self.running = False
                    return
                else:
                    # If an invalid key is pressed, ignore it and continue waiting
                    continue

                # Validate movement within map bounds
                if new_x < 0 or new_x >= game_map.height or new_y < 0 or new_y >= game_map.width:
                    print("Invalid move. Stay within bounds.")
                    self.invalid_move(game_map, x, y)
                    time.sleep(0.3)
                    continue

                # Get the tile at the new position
                tile = game_map.map_data[new_x][new_y]
                tile_symbol = tile.symbol_raw

                # Modular encounter system using a dictionary of encounters
                encounter_handlers = {
                    'E': self.enemy_encounter,
                    'S': self.shrine_encounter,
                    '~': self.invalid_move,
                    '§': self.invalid_move,
                    'B': self.boss_encounter,
                    'N': self.npc_encounter,
                    'V': self.village_encounter,
                    'T': self.treasure_encounter,  # New treasure encounter
                }

                # Initialize moved flag
                moved = False

                # Check if the tile requires an encounter
                if tile_symbol in encounter_handlers:
                    moved = encounter_handlers[tile_symbol](game_map, new_x, new_y)
                else:
                    # If no encounter, move the player
                    game_map.update_player_position(x, y, new_x, new_y)
                    moved = True

                if moved:
                    # Update player position after movement or encounter
                    x, y = new_x, new_y
                    self.hero.player_pos = (x, y)  # Update hero's position

                # Clear the screen and display the updated map
                self.clear()
                game_map.display_map(self.hero)

                # Small delay to prevent multiple key presses being read at once
                time.sleep(0.1)

    def access_inventory(self):
        """Allows the player to view and use items from their inventory."""
        while True:
            self.clear()
            print("Inventory:")
            if not self.hero.items:
                print("Your inventory is empty.")
                input("Press Enter to return to the game.")
                return
            else:
                for idx, item in enumerate(self.hero.items, 1):
                    print(f"{idx}. {item.name} - {item.description}")
                print("Enter the number of the item to use it, or 'b' to go back.")
                choice = input("> ").strip()
                if choice.lower() == 'b':
                    return
                elif choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(self.hero.items):
                        item = self.hero.items.pop(idx)
                        if isinstance(item, Cure):
                            item.use(self.hero)
                            print(f"You used {item.name}.")
                            input("Press Enter to continue.")
                        else:
                            print("You cannot use this item here.")
                            self.hero.items.insert(idx, item)  # Put the item back
                            input("Press Enter to continue.")
                    else:
                        print("Invalid selection.")
                        input("Press Enter to continue.")
                else:
                    print("Invalid input.")
                    input("Press Enter to continue.")

    def enemy_encounter(self, game_map: Map, x: int, y: int) -> bool:
        """Handles encounters with enemies."""
        print("Encountered an enemy!")
        enemy = next((e for e in game_map.enemies if e.pos == (x, y)), None)
        if enemy:
            battle_system = BattleSystem(self.hero, enemy)
            battle_system.start_battle()

            # If enemy is defeated, remove it from the map
            if not enemy.alive:
                game_map.map_data[x][y] = enemy.underlying_tile
                game_map.enemies.remove(enemy)
                self.handle_loot(enemy)

                # Update the player's position on the map after defeating the enemy
                game_map.update_player_position(self.hero.player_pos[0], self.hero.player_pos[1], x, y)
                self.hero.player_pos = (x, y)  # Update hero's position
                return True  # Player moves onto the tile
            else:
                # Player failed to defeat the enemy or escaped
                return False  # Player does not move onto the tile

        else:
            print("Error: Enemy not found at this position.")
            return False

    def boss_encounter(self, game_map: Map, x: int, y: int):
        """Handles encounters with bosses."""
        print("A mighty boss appears!")
        print("\nNEED TO IMPLEMENT IN FUTURE!")
        # Placeholder: Implement boss battle logic here

    def npc_encounter(self, game_map: Map, x: int, y: int):
        """Handles encounters with NPCs."""
        print("You encounter a friendly NPC!")
        print("\nNEED TO IMPLEMENT IN FUTURE!")
        # Placeholder: Implement NPC interaction logic here
    
    def invalid_move(self, game_map: Map, x: int, y: int) -> bool:
        """Handles attempts to move to invalid tiles (e.g., water or lake)."""
        print("You cannot move there.")
        game_map.display_map(self.hero)
        time.sleep(0.3)
        return False  # Player does not move onto the tile
  
    def handle_loot(self, enemy):
        """Handles looting after defeating an enemy."""
        # Handle random item drop
        item = self.enemy_drop_item(enemy)
        if item:
            print(f"The enemy dropped {item.name}!")
            # Add to hero's inventory
            self.hero.items.append(item)
        else:
            print("The enemy did not drop any items.")
        
        # Existing weapon loot code
        print(f"You found {enemy.weapon.name} (Tier: {enemy.tier.capitalize()})(Damage: {enemy.weapon.damage}). Value: {enemy.weapon.value} gold.")
        choice = input("Do you want to pick it up or scrap it for gold? (p/s): ").strip().lower()
        if choice == 'p':
            print(f"You picked up {enemy.weapon.name}.")
            self.hero.equip_weapon(enemy.weapon)
        elif choice == 's':
            print(f"Scrapped {enemy.weapon.name} for {enemy.weapon.value} gold.")
            self.hero.cashpile += enemy.weapon.value
            print(f"Your cashpile now contains {self.hero.cashpile} gold.")
    
    def enemy_drop_item(self, enemy):
        """Determines if an enemy drops an item and returns it."""
        # Modular drop rates
        total_drop_chance = 50  # 50% chance that any item drops
        item_type_chances = {
            'cure': 50,        # If an item drops, 50% chance it's a cure
            'throwable': 50    # If an item drops, 50% chance it's a throwable
        }

        # Determine if an item drops at all
        if rand.randint(1, 100) > total_drop_chance:
            return None  # No item dropped

        # Determine item type
        rand_val = rand.randint(1, 100)
        cumulative = 0
        item_type = None
        for key, chance in item_type_chances.items():
            cumulative += chance
            if rand_val <= cumulative:
                item_type = key
                break

        # Determine item tier based on enemy tier
        tier_map = {
            'low': 'small',
            'mid': rand.choice(['mids', 'midh']),
            'high': 'large',
            'boss': 'superior'
        }
        item_tier = tier_map.get(enemy.tier, 'small')

        # Generate the item
        if item_type == 'cure':
            item = generate_cure(item_tier)
        elif item_type == 'throwable':
            item = generate_throwable(item_tier)
        else:
            item = None

        return item

    def village_encounter(self, game_map: Map, x: int, y: int, visited: bool = False) -> bool:
        """Handles encounters with villages."""
        village_tile = game_map.map_data[x][y]
        self.visited = visited
        if village_tile.visited:
            print("You have already visited this village.")
            time.sleep(1)
            return False  # Do not move onto the tile again
        else:
            print("You have entered a village!")
            self.village_menu()
            # After the village interaction, the player moves onto the village tile
            game_map.update_player_position(self.hero.player_pos[0], self.hero.player_pos[1], x, y)
            self.hero.player_pos = (x, y)
            # Mark the village as visited
            village_tile.visited = True
            village_tile.symbol = f"\033[90mV\033[0m"  # Change to gray color
            village_tile.symbol_raw = 'v'  # Lowercase to indicate visited
            return True  # Player moves onto the tile

    def village_menu(self):
        """Displays the village menu and handles interactions."""
        print("Welcome to the village!")
        visited = False
        while True:
            print("\nVillage Menu:")
            print("1. Rest (heal all HP)")
            print("2. Visit Weapon Shop")
            print("3. Visit Item Shop")
            print("4. Leave Village")
            choice = input("Choose an action: ").strip()
            if choice == '1':
                # Rest and heal the hero
                self.hero.health = self.hero.health_max
                print("You are fully healed!")
                visited = True
            elif choice == '2':
                # Visit the weapon shop
                self.weapon_shop()
                visited = True
            elif choice == '3':
                # Visit the item shop
                self.item_shop()
                visited = True
            elif choice == '4':
                # Leave the village
                print("Leaving the village.")
                break
            else:
                print("Invalid choice. Try again.")


            
    def weapon_shop(self):
        """Handles the weapon shop interactions."""
        print("\nWelcome to the Weapon Shop!")
        # Generate weapons for sale
        weapons_for_sale = (
            [generate_weapon("low") for _ in range(5)] +
            [generate_weapon("mid") for _ in range(4)] +
            [generate_weapon("high") for _ in range(2)]
        )
        # Display available weapons
        for idx, weapon in enumerate(weapons_for_sale, 1):
            print(f"{idx}. {weapon.name} (Tier: {weapon.tier.capitalize()}) - Damage: {weapon.damage} - {weapon.value} gold")
        choice = input("Select a weapon to buy or 'b' to go back: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(weapons_for_sale):
                weapon = weapons_for_sale[idx]
                if self.hero.cashpile >= weapon.value:
                    self.hero.cashpile -= weapon.value
                    self.hero.equip_weapon(weapon)
                    print(f"You bought and equipped {weapon.name}.")
                else:
                    print("You don't have enough gold.")
            else:
                print("Invalid selection.")
        elif choice.lower() == 'b':
            return
        else:
            print("Invalid input.")
        input("Press Enter to continue.")

    def item_shop(self):
        """Handles the item shop interactions."""
        print("\nWelcome to the Item Shop!")
        """Handles the item shop interactions."""
        print("\nWelcome to the Item Shop!")
        # Generate items for sale
        items_for_sale = [
            generate_cure("small"),
            generate_cure("mids"),
            generate_cure("midh"),
            generate_throwable("small"),
            generate_throwable("mids")
        ]
        # Display available items
        for idx, item in enumerate(items_for_sale, 1):
            print(f"{idx}. {item.name} - {item.description} - {item.value} gold")
        choice = input("Select an item to buy or 'b' to go back: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items_for_sale):
                item = items_for_sale[idx]
                if self.hero.cashpile >= item.value:
                    self.hero.cashpile -= item.value
                    self.hero.items.append(item)
                    print(f"You bought {item.name}.")
                else:
                    print("You don't have enough gold.")
            else:
                print("Invalid selection.")
        elif choice.lower() == 'b':
            return
        else:
            print("Invalid input.")
        input("Press Enter to continue.")

    def treasure_encounter(self, game_map: Map, x: int, y: int) -> bool:
        """Handles encounters with treasures."""
        print("You found a treasure chest!")
        # Implement treasure logic here
        # For example, add gold or items to the hero's inventory
        self.hero.cashpile += 100  # Example: add 100 gold
        print("You received 100 gold!")
        # After collecting, remove the treasure from the map
        game_map.map_data[x][y] = game_map.map_data[x][y].underlying_tile
        # Move the player onto the treasure tile
        game_map.update_player_position(self.hero.player_pos[0], self.hero.player_pos[1], x, y)
        self.hero.player_pos = (x, y)
        return True

    def spawn_shrine(self, game_map):
        """Places the shrine on the map at a random location."""
        while True:
            x = rand.randint(1, game_map.height - 2)
            y = rand.randint(1, game_map.width - 2)
            if game_map.map_data[x][y].walkable and game_map.map_data[x][y].symbol_raw not in ['P', 'V']:
                game_map.map_data[x][y] = shrine
                game_map.boss_spawned = True
                print("A mysterious shrine has appeared on the map!")
                time.sleep(2)
                break

    def shrine_encounter(self, game_map: Map, x: int, y: int) -> bool:
        """Handles the shrine encounter leading to a boss battle."""
        print("You have discovered the shrine!")
        boss = generate_boss(self.boss_defeated % len(boss_list))  # Loop through bosses
        battle_system = BattleSystem(self.hero, boss)
        battle_system.start_battle()

        if not self.hero.alive:
            self.handle_game_over()
            return False

        if not boss.alive:
            print(f"You have defeated {boss.name}!")
            # Handle boss drops
            for item_name in boss.drops:
                # Assume we have a method to create items from names
                item = create_item_from_name(item_name)
                self.hero.items.append(item)
                print(f"You received {item.name}!")
            self.boss_defeated += 1
            game_map.clear_map()
            self.display_level_up_message()
            self.start_new_level()
            return True
        return False

    def start_new_level(self):
        """Starts a new level with increased difficulty."""
        self.cycle += 1  # Increment cycle
        print(f"Starting New Game+{self.cycle}")
        self.seed = rand.randint(0, self.MAX_SEED_VALUE)
        print(f"Generating new map with seed: {self.seed}")
        # Create a new map without reinitializing the hero
        self.start_game(new_game=False)

    def display_level_up_message(self):
        """Displays a message after defeating a boss."""
        self.clear()
        print(f"You have defeated {self.boss_defeated} out of {self.total_bosses} bosses.")
        if self.boss_defeated < self.total_bosses:
            print("Prepare yourself for the next challenge!")
        else:
            print("Congratulations! You have defeated all the bosses!")
        input("Press Enter to continue...")

if __name__ == "__main__":
    game = Game()
    game.run()