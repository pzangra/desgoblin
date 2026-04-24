# map_system/tiles.py

import pygame
import os

# ANSI escape sequences for colors
ansi_colors = {
    'reset': '\033[0m',
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
}

class Tile:
    """Class to represent a map tile."""

    tile_types = set()

    def __init__(self, name: str, symbol: str, color: str, colored: bool = True, walkable: bool = True, visited=False):
        self.name = name  # Name used for loading the image (should match the filename)
        self.symbol_raw = symbol
        self.symbol = f"{color}{symbol}{ansi_colors['reset']}" if colored else symbol
        self.walkable = walkable  # Indicates if the tile can be walked on or have enemies
        self.visited = visited    # For tiles like villages that can be visited
        self.image = None 
        self.enemy = None 
        Tile.tile_types.add(name)

def load_image(image_name):
    """Loads an image from the assets/png directory."""
    base_path = os.path.dirname(os.path.dirname(__file__))  # Get the project root directory
    image_path = os.path.join(base_path, 'assets', 'png', f"{image_name}.png")
    if os.path.exists(image_path):
        return pygame.image.load(image_path)  # Load without conversion
    else:
        # Handle missing image file
        print(f"Warning: Image file {image_path} not found.")
        placeholder = pygame.Surface((32, 32))
        placeholder.fill((255, 0, 255))  # Magenta color to indicate missing texture
        return placeholder

def load_tile_images():
    """Loads images for all tiles."""
    # Ensure Pygame is initialized before calling this function
    base_path = os.path.dirname(os.path.dirname(__file__))  # Get the project root directory
    assets_dir = os.path.join(base_path, 'assets', 'png')

    for tile in [plains, forest, brush, mountain, water, lake, desert, swamp, snow, hill, river, beach, cave, ruins, shrine_tile, boss_tile, default, player, village, treasure]:
        image_path = os.path.join(assets_dir, f"{tile.name}.png")
        if os.path.exists(image_path):
            tile.image = pygame.image.load(image_path).convert_alpha()
        else:
            # Handle missing image file
            print(f"Warning: Image file {image_path} not found.")
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta color to indicate missing texture
            tile.image = placeholder

enemy_images = {}

def load_enemy_images():
    """Loads images for enemies."""
    assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'png')
    for tier in ['low', 'mid', 'high']:
        image_path = os.path.join(assets_dir, f"{tier}_enemy.png")
        if os.path.exists(image_path):
            enemy_images[tier] = pygame.image.load(image_path).convert_alpha()
        else:
            print(f"Warning: Enemy image {image_path} not found.")
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 0))  # Red color for missing image
            enemy_images[tier] = placeholder

# Load images for tiles
tile_images = {
    "plains": load_image("plains"),
    "forest": load_image("forest"),
    "brush": load_image("brush"),
    "mountain": load_image("mountain"),
    "water": load_image("water"),
    "lake": load_image("lake"),
    "desert": load_image("desert"),
    "swamp": load_image("swamp"),
    "snow": load_image("snow"),
    "hill": load_image("hill"),
    "river": load_image("river"),
    "beach": load_image("beach"),
    "cave": load_image("cave"),
    "ruins": load_image("ruins"),
    "shrine": load_image("shrine"),
    "boss": load_image("boss"),
    "default": load_image("default"),
    "player": load_image("player"),
    "village": load_image("village"),
    "treasure": load_image("treasure"),
}

# Define tiles with names matching their image filenames
plains = Tile("plains", ";", ansi_colors.get('yellow', ''), walkable=True)
forest = Tile("forest", "8", ansi_colors.get('green', ''), walkable=True)
brush = Tile("brush", "^", ansi_colors.get('magenta', ''), walkable=True)
mountain = Tile("mountain", "A", ansi_colors.get('white', ''), walkable=True)
water = Tile("water", "~", ansi_colors.get('blue', ''), walkable=False)
lake = Tile("lake", "§", ansi_colors.get('cyan', ''), walkable=False)
desert = Tile("desert", ".", ansi_colors.get('bright_yellow', ''), walkable=True)
swamp = Tile("swamp", "&", ansi_colors.get('bright_green', ''), walkable=True)
snow = Tile("snow", "*", ansi_colors.get('bright_white', ''), walkable=True)
hill = Tile("hill", "m", ansi_colors.get('bright_magenta', ''), walkable=True)
river = Tile("river", "≈", ansi_colors.get('bright_blue', ''), walkable=False)
beach = Tile("beach", "_", ansi_colors.get('yellow', ''), walkable=True)
cave = Tile("cave", "C", ansi_colors.get('bright_black', ''), walkable=True)
ruins = Tile("ruins", "R", ansi_colors.get('red', ''), walkable=True)
shrine_tile = Tile("shrine", "S", ansi_colors.get('bright_magenta', ''), walkable=False)
boss_tile = Tile("boss", "B", ansi_colors.get('bright_red', ''), walkable=False)
default = Tile("default", "#", ansi_colors.get('black', ''), walkable=True)
player = Tile("player", "P", ansi_colors.get('green', ''), walkable=False)
village = Tile("village", "V", ansi_colors.get('green', ''), walkable=False, visited=False)
treasure = Tile("treasure", "T", ansi_colors.get('yellow', ''), walkable=False)
treasure_empty = Tile("treasure_empty", "t", ansi_colors.get('yellow', ''), walkable=True)

# Assign images to tiles
plains.image = tile_images["plains"]
forest.image = tile_images["forest"]
brush.image = tile_images["brush"]
mountain.image = tile_images["mountain"]
water.image = tile_images["water"]
lake.image = tile_images["lake"]
desert.image = tile_images["desert"]
swamp.image = tile_images["swamp"]
snow.image = tile_images["snow"]
hill.image = tile_images["hill"]
river.image = tile_images["river"]
beach.image = tile_images["beach"]
cave.image = tile_images["cave"]
ruins.image = tile_images["ruins"]
shrine_tile.image = tile_images["shrine"]
boss_tile.image = tile_images["boss"]
default.image = tile_images["default"]
player.image = tile_images["player"]
village.image = tile_images["village"]
treasure.image = tile_images["treasure"]
treasure_empty.image = load_image("treasure_empty")