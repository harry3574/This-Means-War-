import pygame
from constants import WIDTH, HEIGHT, WHITE, BLACK, GREEN, RED, BLUE, YELLOW, CYAN
from constants import UNICODE_FONT
from database import create_profile, delete_profile, list_profiles, load_game, list_saves, initialize_database
from game_logic import main_game_loop


def draw_text(screen, text, font, color, x, y):
    """Helper function to draw text on the screen."""
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def draw_button(screen, text, font, color, rect, hover=False):
    """Helper function to draw a button."""
    if hover:
        pygame.draw.rect(screen, YELLOW, rect)
    else:
        pygame.draw.rect(screen, WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    draw_text(screen, text, font, color, rect.x + 10, rect.y + 10)

def draw_menu(screen, selected_option, saves=None):
    """Draw the main menu with options."""
    screen.fill(WHITE)
    font = pygame.font.Font(UNICODE_FONT, 48)
    small_font = pygame.font.Font(UNICODE_FONT, 36)

    title = font.render("War Game - Card Swapping Edition", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    options = [
        "1. Start New Game",
        "2. Load Saved Game",
        "3. Save Current Game",
        "4. Exit"
    ]

    y_offset = 250
    for i, option in enumerate(options):
        color = BLUE if i == selected_option else BLACK
        text = small_font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 50

    # Display save files if in load mode
    if saves:
        y_offset += 20
        text = small_font.render("Select a save file to load:", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 40

        for save in saves:
            save_text = f"ID: {save[0]} - Rounds: {save[1]} - Player: {save[2]} - Enemy: {save[3]}"
            text = small_font.render(save_text, True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
            y_offset += 30

    pygame.display.flip()

def profile_creation_menu(screen):
    """Menu for creating a new profile."""
    font = pygame.font.Font(UNICODE_FONT, 36)
    input_text = ""
    active = True

    while active:
        screen.fill(WHITE)
        draw_text(screen, "Enter Profile Name:", font, BLACK, WIDTH // 2 - 150, HEIGHT // 2 - 50)
        draw_text(screen, input_text, font, BLACK, WIDTH // 2 - 100, HEIGHT // 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        create_profile(input_text.strip())
                        return input_text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        pygame.display.flip()

def profile_deletion_menu(screen):
    """Menu for deleting a profile."""
    font = pygame.font.Font(UNICODE_FONT, 36)
    profiles = list_profiles()
    selected_option = 0

    while True:
        screen.fill(WHITE)
        draw_text(screen, "Select a Profile to Delete:", font, BLACK, WIDTH // 2 - 150, 100)

        y_offset = 200
        for i, profile in enumerate(profiles):
            color = BLUE if i == selected_option else BLACK
            text = font.render(f"{profile[0]}. {profile[1]}", True, color)
            screen.blit(text, (WIDTH // 2 - 100, y_offset))
            y_offset += 50

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(profiles)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(profiles)
                elif event.key == pygame.K_RETURN:
                    delete_profile(profiles[selected_option][0])
                    return
                elif event.key == pygame.K_ESCAPE:
                    return

        pygame.display.flip()

def profile_selection_menu():
    """Display the profile selection menu and handle user input."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("War Game - Profile Selection")

    initialize_database()  # Ensure the database is set up

    profiles = list_profiles()
    selected_index = 0  # Track the currently selected profile
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:  # Move to the previous profile
                    selected_index = (selected_index - 1) % len(profiles)
                elif event.key == pygame.K_RIGHT:  # Move to the next profile
                    selected_index = (selected_index + 1) % len(profiles)
                elif event.key == pygame.K_RETURN:  # Select the profile
                    if profiles:
                        selected_profile = profiles[selected_index]
                        main_menu(selected_profile[0])  # Start the game with the selected profile
                        running = False
                elif event.key == pygame.K_ESCAPE:  # Return to the main menu
                    running = False

        draw_profile_selection_menu(screen, profiles, selected_index)
        pygame.display.flip()

    pygame.quit()

def draw_profile_selection_menu(screen, profiles, selected_index):
    """Draw the profile selection menu."""
    screen.fill(WHITE)
    font = pygame.font.Font(UNICODE_FONT, 48)
    small_font = pygame.font.Font(UNICODE_FONT, 36)

    title = font.render("Select a Profile", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    if not profiles:
        text = small_font.render("No profiles found. Create one first!", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
        return

    # Display the selected profile
    selected_profile = profiles[selected_index]
    profile_text = f"{selected_profile[2]} {selected_profile[1]}"  # Emoji + Name
    text = font.render(profile_text, True, BLUE)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 50))

    # Display instructions
    instructions = small_font.render("Use LEFT/RIGHT to switch, ENTER to select, ESC to cancel", True, BLACK)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))

def draw_profile_menu(screen, selected_option, profiles, delete_mode=False, delete_index=0):
    """Draw the profile selection menu."""
    screen.fill(WHITE)

    font = pygame.font.Font(UNICODE_FONT, 48)
    small_font = pygame.font.Font(UNICODE_FONT, 36)


    title = font.render("Select a Profile", True, BLACK)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    options = [
        "1. Create New Profile",
        "2. Delete Profile",
        "3. Select Profile",
        "4. Exit"
    ]

    y_offset = 250
    for i, option in enumerate(options):
        color = BLUE if i == selected_option else BLACK
        text = small_font.render(option, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 50

    # Display profiles
    y_offset += 20
    text = small_font.render("Profiles:", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
    y_offset += 40

    for i, profile in enumerate(profiles):
        profile_text = f"{profile[2]} {profile[1]}"  # Emoji + Name
        color = RED if delete_mode and i == delete_index else BLACK
        text = small_font.render(profile_text, True, color)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y_offset))
        y_offset += 30

    # Display instructions for delete mode
    if delete_mode:
        instructions = small_font.render("Use LEFT/RIGHT to select, ENTER to delete, ESC to cancel", True, BLACK)
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))

    pygame.display.flip()

def profile_menu():
    """Display the profile menu and handle user input."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("War Game - Profile Menu")

    initialize_database()  # Ensure the database is set up

    selected_option = 0
    running = True
    profiles = list_profiles()
    delete_mode = False  # Track whether we're in delete mode
    delete_index = 0  # Track the selected profile for deletion

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if delete_mode:
                    if event.key == pygame.K_LEFT:  # Move to the previous profile
                        delete_index = (delete_index - 1) % len(profiles)
                    elif event.key == pygame.K_RIGHT:  # Move to the next profile
                        delete_index = (delete_index + 1) % len(profiles)
                    elif event.key == pygame.K_RETURN:  # Confirm deletion
                        delete_profile(profiles[delete_index][0])
                        profiles = list_profiles()
                        delete_mode = False
                    elif event.key == pygame.K_ESCAPE:  # Cancel deletion
                        delete_mode = False
                else:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Create New Profile
                            name = input_menu("Create New Profile")
                            if name:
                                create_profile(name)
                                profiles = list_profiles()
                        elif selected_option == 1:  # Delete Profile
                            if profiles:
                                delete_mode = True
                                delete_index = 0
                        elif selected_option == 2:  # Select Profile
                            profile_selection_menu()  # Open the profile selection menu
                            running = False
                        elif selected_option == 3:  # Exit
                            running = False
                            pygame.quit()
                            return

        draw_profile_menu(screen, selected_option, profiles, delete_mode, delete_index)

    pygame.quit()

def main_menu(profile_id):
    """Display the main menu and handle user input for a specific profile."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("War Game - Main Menu")

    selected_option = 0
    running = True
    in_load_mode = False
    saves = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if in_load_mode:
                    if event.key == pygame.K_ESCAPE:  # Exit load mode
                        in_load_mode = False
                        saves = None
                    elif event.key == pygame.K_RETURN:  # Load selected save
                        save_id = saves[selected_option][0]
                        loaded_state = load_game(profile_id, save_id)
                        if loaded_state:
                            main_game_loop(profile_id, loaded_state)
                        else:
                            print("Failed to load save.")
                        in_load_mode = False
                        saves = None
                else:
                    if event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if selected_option == 0:  # Start New Game
                            main_game_loop(profile_id)
                        elif selected_option == 1:  # Load Saved Game
                            saves = list_saves(profile_id)
                            in_load_mode = True
                            selected_option = 0
                        elif selected_option == 2:  # Save Current Game
                            print("Save option selected. Use F5 in-game to save.")
                        elif selected_option == 3:  # Exit
                            running = False
                            pygame.quit()
                            return

        draw_menu(screen, selected_option, saves if in_load_mode else None)

    pygame.quit()

def draw_input_menu(screen, title, input_text, emoji_text):
    """Draw a menu for entering text and emoji."""
    screen.fill(WHITE)
    font = pygame.font.Font(UNICODE_FONT, 48)
    small_font = pygame.font.Font(UNICODE_FONT, 36)

    # Draw title
    title_text = font.render(title, True, BLACK)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

    # Draw input text
    input_label = small_font.render("Name: " + input_text, True, BLACK)
    screen.blit(input_label, (WIDTH // 2 - input_label.get_width() // 2, 250))

    # Draw emoji text
    emoji_label = small_font.render("Emoji: " + emoji_text, True, BLACK)
    screen.blit(emoji_label, (WIDTH // 2 - emoji_label.get_width() // 2, 300))

    # Draw instructions
    instructions = small_font.render("Press ENTER to confirm, ESC to cancel", True, BLACK)
    screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 100))

    pygame.display.flip()

def input_menu(title):
    """Display a menu for entering a profile name."""
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Input Menu")

    input_text = ""
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Confirm input
                    return input_text
                elif event.key == pygame.K_ESCAPE:  # Cancel input
                    return None
                elif event.key == pygame.K_BACKSPACE:  # Delete last character
                    input_text = input_text[:-1]
                else:
                    if event.unicode:  # Add character to input
                        input_text += event.unicode

        draw_input_menu(screen, title, input_text, "")

    pygame.quit()
    return None

if __name__ == "__main__":
    profile_menu()