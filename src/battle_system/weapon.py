# battle_system/weapon.py
import pygame
import os
from random import randint, choice






class Weapon:
    """A class representing a weapon."""

    def __init__(self, name: str, weapon_type: str, damage: int = 0, value: int = 0, tier: str = "low", cycle: int = 0) -> None:
        self.name = name
        self.weapon_type = weapon_type
        self.damage = damage
        self.dmg_min = int(damage * 0.7)  # Minimum damage (70% of base damage)
        self.dmg_max = int(damage * 1.3)  # Maximum damage (130% of base damage)
        self.value = value
        self.tier = tier
        self.cycle = cycle  # Added cycle attribute
        self.image = None

    def get_display_name(self):
        """Returns the weapon name adjusted for the cycle."""
        if self.cycle == 0:
            return self.name
        elif self.cycle == 1:
            return f"{self.name}+"
        else:
            return f"{self.name}+{self.cycle}"

    def load_image(self):
        """Loads the weapon's image."""
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'png', 'weapons')
        image_path = os.path.join(assets_dir, f"{self.name.lower().replace(' ', '_')}.png")
        if os.path.exists(image_path):
            return pygame.image.load(image_path).convert_alpha()
        else:
            return None

def generate_weapon(tier: str, cycle: int = 0) -> Weapon:
    """Generates a weapon based on the specified tier."""
    weapon_lists = {
        "low": low_tier_weapons,
        "mid": mid_tier_weapons,
        "high": high_tier_weapons
    }
    tier_stats = {
        "low": {
            "damage_range": (3, 6),
            "value_range": (5, 10)
        },
        "mid": {
            "damage_range": (7, 12),
            "value_range": (15, 25)
        },
        "high": {
            "damage_range": (13, 20),
            "value_range": (30, 50)
        }
    }
    weapon_list = weapon_lists.get(tier)
    stats = tier_stats.get(tier)
    if not weapon_list or not stats:
        raise ValueError("Invalid tier for weapon generation")

    # Select a random weapon from the tier's weapon list
    weapon_template = choice(weapon_list)
    
    # Generate damage and value within the tier's range
    damage = randint(*stats['damage_range'])
    value = randint(*stats['value_range'])
    # Scale damage and value with cycle
    damage = int(damage * (1 + 0.2 * cycle))
    value = int(value * (1 + 0.2 * cycle))
    # Adjust weapon name
    weapon_name = weapon_template.name
    if cycle == 1:
        weapon_name += '+'
    elif cycle > 1:
        weapon_name += f'+{cycle}'
    # Create the weapon with the adjusted name
    return Weapon(
        name=weapon_name,
        weapon_type=weapon_template.weapon_type,
        damage=damage,
        value=value,
        tier=tier,
        cycle=cycle
    )

# Weapon lists per tier, with Weapon instances containing name and weapon_type

# Low-tier weapons (natural and normal)
low_tier_weapons_norm = [
    Weapon(name="Dagger", weapon_type="sharp"),
    Weapon(name="Club", weapon_type="blunt"),
    Weapon(name="Short Bow", weapon_type="ranged"),
    Weapon(name="Fists", weapon_type="blunt"),
    Weapon(name="Hand Axe", weapon_type="sharp"),
    Weapon(name="Sling", weapon_type="ranged"),
    Weapon(name="Hatchet", weapon_type="sharp"),
    Weapon(name="Wooden Spear", weapon_type="sharp"),
    Weapon(name="Rusty Sword", weapon_type="sharp"),
    Weapon(name="Throwing Stone", weapon_type="blunt")
]
low_tier_weapons_nat = [
    Weapon(name="Bounce", weapon_type="natural"),
    Weapon(name="Tail Whip", weapon_type="natural"),
    Weapon(name="Bites", weapon_type="natural"),
    Weapon(name="Tentacle Slap", weapon_type="natural"),
    Weapon(name="Bone Claws", weapon_type="natural"),
    Weapon(name="Spiked Carapace", weapon_type="natural"),
    Weapon(name="Venomous Fangs", weapon_type="natural"),
    Weapon(name="Corrupted Vine", weapon_type="natural"),
    Weapon(name="Acidic Touch", weapon_type="natural"),
    Weapon(name="Ghoul Claws", weapon_type="natural")
]
low_tier_weapons = low_tier_weapons_norm + low_tier_weapons_nat

# Mid-tier weapons (natural and normal)
mid_tier_weapons_norm = [
    Weapon(name="Iron Sword", weapon_type="sharp"),
    Weapon(name="Scimitar", weapon_type="sharp"),
    Weapon(name="Mace", weapon_type="blunt"),
    Weapon(name="Crossbow", weapon_type="ranged"),
    Weapon(name="Quarterstaff", weapon_type="blunt"),
    Weapon(name="Morningstar", weapon_type="blunt"),
    Weapon(name="Battle Axe", weapon_type="sharp"),
    Weapon(name="Javelin", weapon_type="sharp"),
    Weapon(name="Light Crossbow", weapon_type="ranged"),
    Weapon(name="Flail", weapon_type="blunt")
]
mid_tier_weapons_nat = [
    Weapon(name="Tentacles", weapon_type="natural"),
    Weapon(name="Claws", weapon_type="natural"),
    Weapon(name="Stinger", weapon_type="natural"),
    Weapon(name="Horns", weapon_type="natural"),
    Weapon(name="Pincer", weapon_type="natural"),
    Weapon(name="Eldritch Tendril", weapon_type="natural"),
    Weapon(name="Shadow Bite", weapon_type="natural"),
    Weapon(name="Crawling Chaos Spikes", weapon_type="natural"),
    Weapon(name="Cursed Vine", weapon_type="natural"),
    Weapon(name="Ravenous Maw", weapon_type="natural")
]
mid_tier_weapons = mid_tier_weapons_norm + mid_tier_weapons_nat

# High-tier weapons (natural and normal)
high_tier_weapons_norm = [
    Weapon(name="Long Sword", weapon_type="sharp"),
    Weapon(name="Warhammer", weapon_type="blunt"),
    Weapon(name="Great Hammer", weapon_type="blunt"),
    Weapon(name="Rapier", weapon_type="sharp"),
    Weapon(name="Halberd", weapon_type="sharp"),
    Weapon(name="Heavy Crossbow", weapon_type="ranged"),
    Weapon(name="Double Axe", weapon_type="sharp"),
    Weapon(name="Maul", weapon_type="blunt"),
    Weapon(name="Trident", weapon_type="sharp"),
    Weapon(name="Spiked Chain", weapon_type="blunt")
]
high_tier_weapons_nat = [
    Weapon(name="Acid Spit", weapon_type="natural"),
    Weapon(name="Tail Slam", weapon_type="natural"),
    Weapon(name="Fire Breath", weapon_type="natural"),
    Weapon(name="Necrotic Touch", weapon_type="natural"),
    Weapon(name="Shadow Tentacle", weapon_type="natural"),
    Weapon(name="Eldritch Claw", weapon_type="natural"),
    Weapon(name="Void Strike", weapon_type="natural"),
    Weapon(name="Chaos Bite", weapon_type="natural"),
    Weapon(name="Spectral Fang", weapon_type="natural"),
    Weapon(name="Abyssal Spines", weapon_type="natural")
]
high_tier_weapons = high_tier_weapons_norm + high_tier_weapons_nat