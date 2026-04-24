# battle_system/health_bar.py

import pygame

class HealthBar:
    """Class to represent a health bar for characters."""

    def __init__(self, entity, width: int = 200, height: int = 20, color=(0, 255, 0)):
        self.entity = entity
        self.width = width
        self.height = height
        self.color = color

    def update(self) -> None:
        """Updates the health bar based on the entity's current health."""
        pass  # No additional data to update

    def draw(self, screen, position):
        """Draws the health bar on the screen at the given position."""
        health_ratio = self.entity.health / self.entity.health_max
        pygame.draw.rect(screen, (255, 0, 0), (*position, self.width, self.height))  # Background (red)
        pygame.draw.rect(screen, self.color, (*position, self.width * health_ratio, self.height))  # Health (green)
        # Draw border
        pygame.draw.rect(screen, (255, 255, 255), (*position, self.width, self.height), 2)