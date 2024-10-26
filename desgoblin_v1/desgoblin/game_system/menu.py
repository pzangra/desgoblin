# game_system/menu.py

def display_title():
    """Displays the game title and menu options."""
    print("Welcome to the Chronicles of Desgoblin!")
    print("1. Start Game")
    print("2. Options")
    print("3. Exit")

def handle_menu_input():
    """Handles input from the main menu and returns the player's choice."""
    while True:
        display_title()
        choice = input("> ").strip()
        if choice == "1":
            print("Starting Game...")
            return "1"
        elif choice == "2":
            return "2"  # Return options to set seed or other settings
        elif choice == "3":
            print("Exiting...")
            exit()
        else:
            print("Invalid input. Please enter 1, 2, or 3.")
            input("Press Enter to try again.")

if __name__ == "__main__":
    handle_menu_input()