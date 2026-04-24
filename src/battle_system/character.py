# battle_system/character.py

import pygame
import random
from abc import ABC
from typing import Tuple, TYPE_CHECKING

from battle_system.weapon import Weapon, generate_weapon
from battle_system.health_bar import HealthBar

if TYPE_CHECKING:
    from battle_system.enemy import Enemy
    from battle_system.hero import Hero


class Character(ABC):
    """Base class for all characters in the game."""

    counter_ch: int = 20  # Counter-attack chance percentage

    def __init__(self, name: str, health: int, evade_ch: int, crit_ch: int, armor: int) -> None:
        self.name = name
        self.health = health
        self.health_max = health
        self.evade_ch = evade_ch  # Evade chance percentage
        self.crit_ch = crit_ch  # Critical hit chance percentage
        self.armor = armor  # Damage reduction
        self.weapon = generate_weapon("low")  # Default weapon
        self.health_bar = HealthBar(self, color=(0, 255, 0))  # Default health bar color

    @property
    def alive(self) -> bool:
        """Returns True if the character is alive."""
        return self.health > 0

    def attack(self, target: 'Character', attack_type="normal", is_counter: bool = False) -> str:
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