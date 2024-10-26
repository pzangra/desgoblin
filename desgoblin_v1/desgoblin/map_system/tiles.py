# map_system/tiles.py

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

    def __init__(self, symbol: str, color: str, colored: bool = True, walkable: bool = True, visited = False):
        self.symbol_raw = symbol
        self.symbol = f"{color}{symbol}{ansi_colors['reset']}" if colored else symbol
        self.walkable = walkable  # Indicates if the tile can be walked on or have enemies
        self.visited = visited    # For tiles like villages that can be visited

# Terrain tiles
plains = Tile(";", ansi_colors['yellow'], walkable=True)
forest = Tile("8", ansi_colors['green'], walkable=True)
brush = Tile("^", ansi_colors['magenta'], walkable=True)
mountain = Tile("A", ansi_colors['white'], walkable=True)   # Now walkable
water = Tile("~", ansi_colors['blue'], walkable=False)      # Impassable terrain
lake = Tile("§", ansi_colors['cyan'], walkable=False)       # Impassable terrain
desert = Tile(".", ansi_colors['bright_yellow'], walkable=True)
swamp = Tile("&", ansi_colors['bright_green'], walkable=True)
snow = Tile("*", ansi_colors['bright_white'], walkable=True)
hill = Tile("m", ansi_colors['bright_magenta'], walkable=True)
river = Tile("≈", ansi_colors['bright_blue'], walkable=False)
beach = Tile("_", ansi_colors['yellow'], walkable=True)
cave = Tile("C", ansi_colors['bright_black'], walkable=True)
ruins = Tile("R", ansi_colors['red'], walkable=True)
shrine = Tile("S", ansi_colors['bright_magenta'], walkable=False)
default = Tile("#", ansi_colors['black'], walkable=True)
player = Tile("P", ansi_colors['green'], walkable=False)
village = Tile("V", ansi_colors['green'], walkable=False, visited=False)
treasure = Tile("T", ansi_colors['yellow'], walkable=False)