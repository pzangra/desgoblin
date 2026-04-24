# game_system/menu.py

import pygame
import sys
import os

# Initialize Pygame font
pygame.font.init()

def handle_menu_input():
    """Handles menu input using Pygame with a framerate limit."""
    menu_running = True
    clock = pygame.time.Clock()  # Create a clock for controlling framerate

    while menu_running:
        # Fill screen with background color
        pygame.display.get_surface().fill((100, 100, 100))  # Changed to a shade of gray for visibility

        # Display menu options
        font = pygame.font.Font(None, 36)
        menu_text = [
            "1. New Game",
            "2. Set Seed Game",
            "3. Exit"
        ]
        y = 150
        for line in menu_text:
            text_surface = font.render(line, True, (255, 255, 255))
            pygame.display.get_surface().blit(text_surface, (100, y))
            y += 50

        pygame.display.flip()  # Update the display

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "1"
                elif event.key == pygame.K_2:
                    return "2"
                elif event.key == pygame.K_3:
                    return "3"

        # Limit the framerate to avoid excessive CPU usage
        clock.tick(30)  # Limit to 30 frames per second