from abc import ABC
from typing import Tuple
import random
from battle_system.weapon import Weapon, generate_weapon
from battle_system.health_bar import HealthBar
from battle_system.weapon import *

class Character(ABC):
    """Base class for all characters in the game."""

    counter_ch: int = 20  # Counter-attack chance percentage

    def __init__(self, name: str, health: int, evade_ch: int, crit_ch: int, armor: int) -> None:
        self.name = name
        self.health = health
        self.health_max = health
        self.evade_ch = evade_ch  # Evade chance percentage
        self.crit_ch = crit_ch    # Critical hit chance percentage
        self.armor = armor        # Damage reduction
        self.weapon = generate_weapon("low")  # Default weapon
        self.health_bar = HealthBar(self, color="default")

    @property
    def alive(self) -> bool:
        """Returns True if the character is alive."""
        return self.health > 0

    def attack(self, target, attack_type="normal", is_counter: bool = False) -> str:
        """Performs an attack on the target."""
        messages = []

        if not self.alive:
            messages.append(f"{self.name} cannot attack because they are defeated.")
            return "\n".join(messages)

        if self.roll_event(target.evade_ch):
            messages.append(f"{target.name} evaded the attack!")
            return "\n".join(messages)

        base_damage = self.calculate_base_damage(attack_type)
        damage_after_crit, crit_message = self.deal_crit(base_damage)
        if crit_message:
            messages.append(crit_message)
        final_damage = max(damage_after_crit - target.armor, 1)

        target.take_damage(final_damage)
        messages.append(f"{self.name} attacked {target.name} with {self.weapon.name} for {final_damage} damage.")

        # Counter-attack logic
        if not is_counter and target.alive and self.roll_event(target.counter_ch):
            messages.append(f"{target.name} initiated a counter-attack!")
            counter_attack_info = target.attack(self, is_counter=True)
            messages.append(counter_attack_info)

        return "\n".join(messages)

    def calculate_base_damage(self, attack_type="normal") -> int:
        """Calculates base damage based on attack type."""
        min_damage = int(self.weapon.damage * 0.6) if attack_type == "quick" else int(self.weapon.damage * 0.8)
        max_damage = int(self.weapon.damage * 1.5) if attack_type == "heavy" else int(self.weapon.damage * 1.2)
        if max_damage <= min_damage:
            max_damage = min_damage + 1
        return random.randint(min_damage, max_damage)

    @staticmethod
    def roll_event(chance: int) -> bool:
        """Determines if an event occurs based on chance percentage."""
        return random.randint(1, 100) <= chance

    # In the Character class
    def deal_crit(self, base_damage: int) -> Tuple[int, str]:
        """Calculates critical hit damage."""
        if self.roll_event(self.crit_ch):
            crit_damage = int(base_damage * 1.5)
            crit_message = f"Critical hit! {self.name} deals {crit_damage} damage!"
            return crit_damage, crit_message
        return base_damage, ""

    def take_damage(self, damage: int) -> None:
        """Applies damage to the character."""
        self.health -= damage
        self.health = max(self.health, 0)
        self.health_bar.update()

class Hero(Character):
    """Player-controlled hero character."""

    def __init__(self, name: str, health: int):        
        super().__init__(name=name, health=health, evade_ch=10, crit_ch=15, armor=5)
        self.cashpile = 0
        self.items = []         # Inventory for consumable items
        self.equipment = []     # Inventory for equipment (armor, accessories)
        self.weapon = Weapon(name="Fists", weapon_type="blunt", damage=2, value=0)
        self.health_bar = HealthBar(self, color="green")
        self.player_pos = (1, 1)
        self.level = 1
        self.experience = 0
        self.experience_to_next_level = 100
 
    def attack(self, target, attack_type="normal", is_counter: bool = False) -> str:
        """Performs an attack on the target."""
        messages = []

        if not self.alive:
            messages.append(f"{self.name} cannot attack because they are defeated.")
            return "\n".join(messages)

        if self.roll_event(target.evade_ch):
            messages.append(f"{target.name} evaded the attack!")
            return "\n".join(messages)

        base_damage = self.calculate_base_damage(attack_type)
        damage_after_crit, crit_message = self.deal_crit(base_damage)
        if crit_message:
            messages.append(crit_message)
        final_damage = max(damage_after_crit - target.armor, 1)

        target.take_damage(final_damage)
        messages.append(f"{self.name} attacked {target.name} with {self.weapon.name} for {final_damage} damage.")

        # Counter-attack logic
        if not is_counter and target.alive and self.roll_event(target.counter_ch):
            messages.append(f"{target.name} initiated a counter-attack!")
            counter_attack_info = target.attack(self, is_counter=True)
            messages.append(counter_attack_info)

        return "\n".join(messages)
    
    def equip_weapon(self, new_weapon: Weapon) -> None:
        # Add current weapon's value to cashpile before switching
        self.cashpile += self.weapon.value
        print(f"Scrapped your previous weapon '{self.weapon.name}' for {self.weapon.value} gold.")
        # Equip the new weapon
        self.weapon = new_weapon
        print(f"You equipped '{self.weapon.name}' (Tier: {self.get_weapon_tier(self.weapon)})") 
    
    def gain_experience(self, amount):
        """Adds experience points and checks for level up."""
        self.experience += amount
        print(f"{self.name} gained {amount} experience points.")
        while self.experience >= self.experience_to_next_level:
            self.level_up()

    def get_weapon_tier(self, weapon: Weapon) -> str:
        """Determine weapon tier based on weapon name"""
        if weapon.name in [w.name for w in low_tier_weapons]:
            return "Low"
        elif weapon.name in [w.name for w in mid_tier_weapons]:
            return "Mid"
        elif weapon.name in [w.name for w in high_tier_weapons]:
            return "High"
        return "Unknown"

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


class Enemy(Character):
    """Enemy characters controlled by the game."""

    def __init__(self, name: str, health: int, weapon: Weapon, evade_ch: int, crit_ch: int, armor: int, tier: str) -> None:
        super().__init__(name=name, health=health, evade_ch=evade_ch, crit_ch=crit_ch, armor=armor)
        self.weapon = weapon
        self.health_bar = HealthBar(self, color="red")
        self.tier = tier            # Enemy's tier (low, mid, high)
        self.pos = None             # Position on the map
        self.underlying_tile = None # Tile beneath the enemy (for map updates)

    def set_position(self, x: int, y: int, underlying_tile):
        """Sets the enemy's position on the map."""
        self.pos = (x, y)
        self.underlying_tile = underlying_tile

    def drop_loot(self):
        """Defines the loot dropped by the enemy upon defeat."""
        # You can expand this method to include items or gold
        return self.weapon
    
    def scale_stats(self, multiplier):
        """Scales the enemy's stats by the given multiplier."""
        self.health = int(self.health * multiplier)
        self.health_max = self.health
        self.weapon.damage = int(self.weapon.damage * multiplier)
        self.armor = int(self.armor * multiplier)