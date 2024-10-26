# battle_system/battlesys.py

import random
import os
from battle_system.character import Hero, Enemy
from battle_system.health_bar import HealthBar
from battle_system.item import *

class BattleSystem:
    """Class to manage battles between the hero and enemies."""

    def __init__(self, hero: Hero, enemy: Enemy):
        self.hero = hero
        self.enemy = enemy
        self.running = True
        self.battle_log = [] #initialize battle log

    def start_battle(self):
        """Starts the battle loop."""
        self.hero.health_bar.update()
        self.enemy.health_bar.update()
        self.clear_screen()

        while self.running and self.hero.alive and self.enemy.alive:
            # Display battle status
            self.display_battle_status()

            # Player's turn
            action = input("\nChoose your action: [a]ttack, [s]kills, [i]tems, [e]scape: ").strip().lower()

            if action == 'a':
                self.attack()
            elif action == 's':
                self.use_skill()
            elif action == 'i':
                self.use_item()
            elif action == 'e':
                if self.escape():
                    break
            else:
                self.battle_log.append("Invalid action. Choose again.")
                continue

            # Enemy's turn if still alive
            if self.enemy.alive and self.running:
                self.enemy_attack()

            # Check for end of battle
            if not self.hero.alive:
                self.battle_log.append("You have been defeated! Game Over.")
                self.running = False
                exit()
            elif not self.enemy.alive:
                self.battle_log.append(f"{self.enemy.name} has been defeated!")
                experience_gained = self.calculate_experience(self.enemy)
                self.hero.gain_experience(experience_gained)
                self.running = False

    def display_battle_status(self):
        """Displays the current status of the battle."""
        self.clear_screen()
        print(f"{self.hero.name} HP: {self.hero.health}/{self.hero.health_max} | Weapon: {self.hero.weapon.name} (Damage: {self.hero.weapon.damage}) | Cash: {self.hero.cashpile}")
        self.hero.health_bar.draw()
        print(f"{self.enemy.name} HP: {self.enemy.health}/{self.enemy.health_max} | Weapon: {self.enemy.weapon.name} (Damage: {self.enemy.weapon.damage})")
        self.enemy.health_bar.draw()
        print("\nBattle Log:")
        for log_entry in self.battle_log[-5:]:  # Display the last 5 entries
            print(log_entry)
    
    def attack(self):
        """Handles the hero's attack action."""
        damage_info = self.hero.attack(self.enemy)
        self.battle_log.append(damage_info)

    def use_skill(self):
        """Handles the hero's skill usage."""
        print("\nSkill system is under development.")
        input("Press Enter to continue.")

    def use_item(self):
        """Handles the hero using an item."""
        if not self.hero.items:
            print("You have no items to use.")
            input("Press Enter to continue.")
            return
        print("\nItems:")
        for idx, item in enumerate(self.hero.items, 1):
            print(f"{idx}. {item.name} - {item.description}")
        choice = input("Select an item to use or 'b' to go back: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.hero.items):
                item = self.hero.items.pop(idx)
                item.use(self.hero)
                print(f"You used {item.name}.")
            else:
                print("Invalid selection.")
        elif choice.lower() == 'b':
            return
        else:
            print("Invalid input.")
        input("Press Enter to continue.")

    def escape(self):
        """Attempts to escape from the battle."""
        escape_chance = {"low": 60, "mid": 40, "high": 20}
        chance = escape_chance.get(self.enemy.tier, 0)
        if random.randint(1, 100) <= chance:
            print("Escape successful!")
            self.running = False
            return True
        else:
            print("Escape failed!")
            return False

    def enemy_attack(self):
        """Handles the enemy's attack action."""
        damage_info = self.enemy.attack(self.hero)
        self.battle_log.append(damage_info)

    def calculate_experience(self, enemy):
        """Calculates experience gained from defeating an enemy."""
        tier_experience = {"low": 50, "mid": 100, "high": 200}
        return tier_experience.get(enemy.tier, 0)

    def use_item(self):
        """Handles the hero using an item."""
        if not self.hero.items:
            print("You have no items to use.")
            input("Press Enter to continue.")
            return

        print("\nItems:")
        for idx, item in enumerate(self.hero.items, 1):
            print(f"{idx}. {item.name} - {item.description}")
        choice = input("Select an item to use or 'b' to go back: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.hero.items):
                item = self.hero.items.pop(idx)
                if isinstance(item, Cure):
                    item.use(self.hero)
                elif isinstance(item, Throwable):
                    item.use(self.enemy)
                else:
                    print("Item cannot be used.")
                input("Press Enter to continue.")
            else:
                print("Invalid selection.")
        elif choice.lower() == 'b':
            return
        else:
            print("Invalid input.")
            input("Press Enter to continue.")

    def clear_screen(self):
        """Clears the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        """Clears the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')