# battle_system/enemy.py

from random import choice, randint
import pygame
import os
import random

from battle_system.character import Character
from battle_system.weapon import Weapon, generate_weapon
from battle_system.item import create_item_from_name
from battle_system.health_bar import HealthBar

enemy_names = {
    "low": [
        "Slime", "Rat", "Goblin", "Spider", "Bat", "Snake", "Kobold", "Imp", "Bandit",
        "Skeleton", "Zombie", "Giant Rat", "Cave Beetle", "Mud Crab", "Shadow Cat", "Wild Dog",
        "Giant Centipede", "Boggart", "Mimicling", "Pixie", "Grelling", "Dust Mephit", "Giant Spider",
        "Stirge", "Ghoul", "Darkling", "Wisp", "Crowfolk", "Carrion Beetle", "Vermling", "Giant Ant",
        "Kappa", "Mud Elemental", "Scavenger", "Fire Beetle", "Crimson Bat", "Hagling", "Feral Boar",
        "Dire Rabbit", "Raven", "Young Harpy", "Wood Sprite", "Giant Snail", "Frost Beetle", "Shade",
        "Cursed Doll", "Gloomling", "Thornling", "Drudge", "Forest Imp", "Scarecrow", "Gutter Rat",
        "Young Basilisk", "Giant Leech", "Dark Fairy", "Ash Crawler", "Thieving Monkey", "Dire Mole",
        "Muck Dweller", "Fungal Sprite", "Will-o'-Rat", "Briar Beast", "Rusted Automaton", "Rotten Hound",
        "Pond Scum", "Grave Mite", "Lesser Djinn", "Hedge Gremlin", "Nettle Stalker", "Wicker Man",
        "Black Cat", "Lesser Kobold", "Gloom Bat", "Mist Lurker", "Bog Imp", "Weasel", "Hedgehog",
        "Ragged Ghoul", "Young Hobgoblin", "Firefly Swarm", "Ashen Wisp", "Plague Rat", "Grotto Crab",
        "Dire Toad", "Crag Lizard", "Bramble Elemental", "Shadow Hare", "Sewer Slime", "Wild Goat",
        "Rubble Sprite", "Rock Grub", "Night Roach", "Giant Worm", "Lost Soul", "Gutter Snipe",
        "Broken Puppet"
    ],
    "mid": [
        "Big Goblin", "Hobgoblin", "Orc", "Gnoll", "Wight", "Troll", "Ogre", "Minotaur", "Centaur",
        "Werewolf", "Harpy", "Griffon", "Cyclops", "Gargoyle", "Rakshasa", "Sea Hag", "Doppelganger",
        "Dark Knight", "Redcap", "Chimera", "Banshee", "Dire Wolf", "Will-o'-Wisp", "Revenant", "Barghest",
        "Manticore", "Gorgon", "Siren", "Dryad", "Basilisk", "Cursed Armor", "Grendel", "Bone Naga",
        "Keres", "Anubian Guardian", "Fomorian", "Kelpie", "Wendigo", "Blood Hunter", "Nymph", "Spriggan",
        "Werebear", "Wyrmling", "Shadow Mastiff", "Peryton", "Phantom Knight", "Headless Horseman",
        "Sand Wraith", "Storm Elemental", "Spectral Archer", "Voidwalker", "Night Hag", "Ghoul Lord",
        "Moroi", "Ghul", "Stone Golem", "Hellhound", "Ashen Revenant", "Pit Fiendling", "Fire Djinn",
        "Crocotta", "Ceryneian Hind", "Myrmidon", "Bog Witch", "Fiery Salamander", "Onyx Gargoyle",
        "Frost Troll", "Infernal Imp", "Cave Troll", "Sewer King", "Giant Scorpion", "Silverback Ape",
        "Myrkalfar", "Black Annis", "Ash Wraith", "Desert Ghoul", "Clockwork Soldier", "Vodyanoi",
        "Rusalka", "Draugr", "Half-Orc Brute", "Hill Giant", "Fenrir Pup", "Marble Statue", "Bugbear",
        "Horned Devil", "Spectral Swordsman", "Harlequin Shade", "Cacodaemon", "Gloom Weaver",
        "Blood Shade", "Black Knight"
    ],
    "high": [
        "Wyvern", "Drake", "Titan", "Lich", "Vampire", "Dragon", "Behemoth", "Balor", "Kraken",
        "Nightmare", "Elder Brain", "Shoggoth", "Star Spawn", "Demon Lord", "Pit Fiend", "Moloch",
        "Hydra", "Hellhound Alpha", "Aboleth", "Elder Deep One", "Phoenix", "Archdemon", "Leviathan",
        "Seraphim", "Bone Dragon", "Storm Giant", "Sphinx", "Charybdis", "Scylla", "Thanatos",
        "Hecatoncheires", "Tarrasque", "Frost Wyrm", "Chernobog", "Anubis", "Fenrir", "Jormungandr",
        "Nemean Lion", "Yamata-no-Orochi", "Ifrit", "Djinn Lord", "Nephilim", "Archon", "Astaroth",
        "Beelzebub", "Belial", "Asmodeus", "Lilith", "Ziz", "Mammon", "Azazel", "Bael", "Qliphoth Beast",
        "The Black Goat", "Great Unclean One", "Prince of Darkness", "Yaldabaoth", "Abyssal Wyrm",
        "Ereshkigal", "Vritra", "Kali", "Garuda", "Ravana", "The Morrigan", "Baphomet", "Chimera Prime",
        "Typhon", "Echidna", "Pontianak", "Black Tortoise", "Gugalanna", "Zuul", "Kukulkan", "The Erlking",
        "Archlich", "Death Knight", "Lord of Change", "Archfiend", "Ashura", "Demogorgon", "Nyarlathotep",
        "Ithaqua", "Yog-Sothoth", "Cthulhu", "Apep", "Set", "Geryon", "Aegir", "Kronos", "Hyperion",
        "Atlas", "The Sorrow", "Father of Serpents", "Celestial Dragon", "The Devourer", "The False Prophet"
    ]
}

class Enemy(Character):
    """Enemy characters controlled by the game."""

    def __init__(self, name: str, health: int, weapon: Weapon, evade_ch: int, crit_ch: int, armor: int, tier: str) -> None:
        super().__init__(name=name, health=health, evade_ch=evade_ch, crit_ch=crit_ch, armor=armor)
        self.weapon = weapon
        self.health_bar = HealthBar(self, color=(255, 0, 0))
        self.tier = tier  # Enemy's tier (low, mid, high)
        self.pos = None  # Position on the map
        self.underlying_tile = None  # Tile beneath the enemy (for map updates)

        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'png')
        
        enemy_image_name = f"{self.tier}_enemy.png"
        image_path = os.path.join(assets_dir, enemy_image_name)

        TILE_SIZE = 16

        # Load the enemy sprite image based on the tier
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'png')
        enemy_image_name = f"{self.tier}_enemy.png"
        image_path = os.path.join(assets_dir, enemy_image_name)

        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))  # Scale to tile size
        else:
            print(f"Warning: Enemy image file {enemy_image_name} not found.")
            # Use a placeholder image if the specific enemy image is missing
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255))  # Use magenta color to indicate missing texture

    def set_position(self, x: int, y: int, underlying_tile):
        """Sets the enemy's position on the map."""
        self.pos = (x, y)
        self.underlying_tile = underlying_tile

    def drop_loot(self):
        """Defines the loot dropped by the enemy upon defeat."""
        return self.weapon

    def scale_stats(self, multiplier):
        """Scales the enemy's stats by the given multiplier."""
        self.health = int(self.health * multiplier)
        self.health_max = self.health
        self.weapon.damage = int(self.weapon.damage * multiplier)
        self.armor = int(self.armor * multiplier)


def generate_enemy(tier: str, cycle: int = 0) -> Enemy:
    """Generates an enemy based on the specified tier."""
    names = enemy_names.get(tier)
    if not names:
        raise ValueError("Invalid tier for enemy generation")
    name = choice(names)
    health_ranges = {
        "low": (10, 30),
        "mid": (40, 80),
        "high": (80, 120)
    }
    evade_ch_ranges = {
        "low": (0, 5),
        "mid": (5, 10),
        "high": (10, 15)
    }
    crit_ch_ranges = {
        "low": (5, 8),
        "mid": (8, 12),
        "high": (12, 20)
    }
    armor_ranges = {
        "low": (0, 2),
        "mid": (2, 6),
        "high": (6, 12)
    }

    # Assign initial values
    health = randint(*health_ranges[tier])
    evade_ch = randint(*evade_ch_ranges[tier])
    crit_ch = randint(*crit_ch_ranges[tier])
    armor = randint(*armor_ranges[tier])


     # Scale stats based on cycle
    health = int(health * (1 + 0.2 * cycle))
    evade_ch = int(evade_ch * (1 + 0.1 * cycle))
    crit_ch = int(crit_ch * (1 + 0.1 * cycle))
    armor = int(armor * (1 + 0.1 * cycle))
    weapon = generate_weapon(tier, cycle)
    # Create the enemy with adjusted stats
    enemy = Enemy(
        name=name,
        health=health,
        weapon=weapon,
        evade_ch=evade_ch,
        crit_ch=crit_ch,
        armor=armor,
        tier=tier
    )
    # Set image filename for the enemy based on tier
    enemy.image_filename = f"{tier}_enemy.png"
    return enemy



class Boss(Enemy):
    """Boss characters with special abilities."""

    def __init__(self, name, health, weapon, evade_ch, crit_ch, armor, tier, skills, drops):
        super().__init__(name, health, weapon, evade_ch, crit_ch, armor, tier)
        self.skills = skills
        self.drops = drops

        # Load boss sprite
        try:
            self.sprite = pygame.image.load('assets/png/boss_enemy.png')  # Update path if needed
        except FileNotFoundError:
            print("Warning: Boss sprite not found. Using default placeholder.")
            self.sprite = None

    def choose_action(self):
        """Chooses an action for the boss to take."""
        # For now, the boss only attacks
        actions = ["attack"]  # You can expand this list to include more actions like 'skill' in the future
        return random.choice(actions)

    def take_damage(self, damage):
        """Reduces the boss's health by the specified damage."""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False

boss_list = [
    {
        'name': 'Dragon Lord',
        'health': 300,
        'weapon': Weapon(name='Flame Breath', weapon_type='natural', damage=50),
        'evade_ch': 10,
        'crit_ch': 20,
        'armor': 15,
        'tier': 'boss',
        'skills': ['Firestorm', 'Tail Swipe'],
        'drops': ['Legendary Sword', 'Dragon Scale']
    },
    # Define other bosses similarly...
]

def generate_boss(boss_index):
    """Generates a boss based on the index in the boss list."""
    boss_data = boss_list[boss_index]
    boss = Boss(
        name=boss_data['name'],
        health=boss_data['health'],
        weapon=boss_data['weapon'],
        evade_ch=boss_data['evade_ch'],
        crit_ch=boss_data['crit_ch'],
        armor=boss_data['armor'],
        tier=boss_data['tier'],
        skills=boss_data['skills'],
        drops=boss_data['drops']
    )
    return boss