# battle_system/battlesys.py

import random
import os, sys
import pygame
from battle_system.hero import Hero
from battle_system.enemy import Enemy
from battle_system.health_bar import HealthBar
from battle_system.item import *

class BattleSystem:
    """Class to manage battles between the hero and enemies."""

    def __init__(self, hero: Hero, enemy: Enemy):
        self.hero = hero
        self.enemy = enemy
        self.running = True
        self.battle_log = []  # Initialize battle log

        # Initialize Pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Battle")

        self.clock = pygame.time.Clock()

        # Load fonts
        self.font = pygame.font.SysFont('Arial', 20)
        self.font_large = pygame.font.SysFont('Arial', 30)

        # Load images
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'png')
        self.hero_image = pygame.image.load(os.path.join(assets_dir, 'player.png')).convert_alpha()
        self.enemy_image = pygame.image.load(os.path.join(assets_dir, f"{self.enemy.tier}_enemy.png")).convert_alpha()

        # Scale images
        self.hero_image = pygame.transform.scale(self.hero_image, (128, 128))
        self.enemy_image = pygame.transform.scale(self.enemy_image, (128, 128))

    def start_battle(self):
        """Starts the battle loop."""
        self.hero.health_bar.update()
        self.enemy.health_bar.update()

        while self.running and self.hero.alive and self.enemy.alive:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        if not self.hero.alive:
            self.battle_log.append("You have been defeated! Game Over.")
            self.running = False
            # Handle game over logic
        elif not self.enemy.alive:
            self.battle_log.append(f"{self.enemy.name} has been defeated!")
            experience_gained = self.calculate_experience(self.enemy)
            self.hero.gain_experience(experience_gained)
            self.running = False

    def handle_events(self):
        """Handles Pygame events during battle."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.attack()
                    if self.enemy.alive:
                        self.enemy_attack()
                elif event.key == pygame.K_s:
                    self.use_skill()
                elif event.key == pygame.K_i:
                    self.use_item()
                elif event.key == pygame.K_e:
                    if self.escape():
                        self.running = False

    def update(self):
        """Updates game state."""
        pass  # For now, no additional state to update

    def draw(self):
        """Draws the battle screen."""
        self.screen.fill((0, 0, 0))  # Clear screen

        # Draw hero
        self.screen.blit(self.hero_image, (100, 250))
        self.hero.health_bar.draw(self.screen, (100, 220))
        hero_name_text = self.font_large.render(self.hero.name, True, (255, 255, 255))
        self.screen.blit(hero_name_text, (100, 190))

        # Draw enemy
        self.screen.blit(self.enemy_image, (500, 100))
        self.enemy.health_bar.draw(self.screen, (500, 70))
        enemy_name_text = self.font_large.render(self.enemy.name, True, (255, 255, 255))
        self.screen.blit(enemy_name_text, (500, 40))

        # Draw battle log
        y_offset = 450
        for log_entry in self.battle_log[-5:]:
            log_text = self.font.render(log_entry, True, (255, 255, 255))
            self.screen.blit(log_text, (50, y_offset))
            y_offset += 20

        # Draw instructions
        instructions = self.font.render("Press 'A' to Attack, 'S' for Skills, 'I' for Items, 'E' to Escape", True, (255, 255, 0))
        self.screen.blit(instructions, (50, 20))

        pygame.display.flip()

    def attack(self):
        """Handles the hero's attack action."""
        damage_info = self.hero.attack(self.enemy)
        self.battle_log.append(damage_info)

    def use_skill(self):
        """Handles the hero's skill usage."""
        self.battle_log.append("Skills are under development.")

    def use_item(self):
        """Handles the hero using an item."""
        if not self.hero.items:
            self.battle_log.append("You have no items to use.")
            return

        # For simplicity, we'll use the first item
        item = self.hero.items.pop(0)
        if isinstance(item, Cure):
            item.use(self.hero)
        elif isinstance(item, Throwable):
            item.use(self.enemy)
        self.battle_log.append(f"You used {item.name}.")

    def escape(self):
        """Attempts to escape from the battle."""
        escape_chance = {"low": 60, "mid": 40, "high": 20}
        chance = escape_chance.get(self.enemy.tier, 0)
        if random.randint(1, 100) <= chance:
            self.battle_log.append("Escape successful!")
            return True
        else:
            self.battle_log.append("Escape failed!")
            self.enemy_attack()
            return False

    def enemy_attack(self):
        """Handles the enemy's attack action."""
        damage_info = self.enemy.attack(self.hero)
        self.battle_log.append(damage_info)

    def calculate_experience(self, enemy):
        """Calculates experience gained from defeating an enemy."""
        tier_experience = {"low": 50, "mid": 100, "high": 200}
        return tier_experience.get(enemy.tier, 0)