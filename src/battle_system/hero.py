# battle_system/hero.py
import pygame

from battle_system.character import Character
from battle_system.weapon import Weapon
from battle_system.health_bar import HealthBar


class Hero(Character):
    """Player-controlled hero character."""

    def __init__(self, name: str, health: int):
        super().__init__(name=name, health=health, evade_ch=10, crit_ch=15, armor=5)
        self.cashpile = 0
        self.items = []         # Inventory for consumable items
        self.equipment = []     # Inventory for equipment (armor, accessories)
        self.weapon = Weapon(name="Fists", weapon_type="blunt", damage=2, value=0)
        self.health_bar = HealthBar(self, color=(0, 255, 0))
        self.player_pos = (1, 1)
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100

        # Load hero sprite
        try:
            self.sprite = pygame.image.load('assets/png/hero.png')  # Update path if needed
        except FileNotFoundError:
            print("Warning: Hero sprite not found. Using default placeholder.")
            self.sprite = None

    def gain_experience(self, amount):
        """Adds experience points and checks for level up."""
        self.experience += amount
        print(f"{self.name} gained {amount} experience points.")
        while self.experience >= self.experience_to_next_level:
            self.level_up()

    def level_up(self):
        """Levels up the hero, increasing stats."""
        self.experience -= self.experience_to_next_level
        self.level += 1
        self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
        self.health_max += 10
        self.health = self.health_max
        self.evade_ch += 1
        self.crit_ch += 1
        self.armor += 1
        print(f"{self.name} leveled up to level {self.level}!")
        print("Stats increased: Health +10, Evade Chance +1%, Crit Chance +1%, Armor +1")

    def equip_weapon(self, new_weapon: Weapon) -> None:
        """Equips a new weapon, replacing the current one."""
        # Add current weapon's value to cashpile before switching
        self.cashpile += self.weapon.value
        print(f"Scrapped your previous weapon '{self.weapon.name}' for {self.weapon.value} gold.")
        # Equip the new weapon
        self.weapon = new_weapon
        print(f"You equipped '{self.weapon.name}' (Tier: {self.get_weapon_tier(self.weapon)})")

    def get_weapon_tier(self, weapon: Weapon) -> str:
        """Determine weapon tier based on weapon name"""
        # Implement logic to determine weapon tier
        return weapon.tier.capitalize()