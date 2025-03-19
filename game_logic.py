import pygame
from collections import Counter
from constants import WIDTH, HEIGHT, WHITE, BLACK, GREEN, RED, BLUE, YELLOW, CYAN, UNICODE_FONT
from deck import create_deck, shuffle_deck, split_deck
from card_utils import draw_card, compare_cards
import json
from pathlib import Path

SAVE_FILE = "game_save.json"

'''
for .json
def save_game(player_deck, enemy_deck, player_score, enemy_score, total_rounds, player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards):
    """Save the current game state to a file."""
    game_state = {
        "player_deck": player_deck,
        "enemy_deck": enemy_deck,
        "player_score": player_score,
        "enemy_score": enemy_score,
        "total_rounds": total_rounds,
        "player_wins": player_wins,
        "enemy_wins": enemy_wins,
        "ties": ties,
        "cards_played": cards_played,
        "win_streak": win_streak,
        "longest_win_streak": longest_win_streak,
        "played_cards": played_cards,
    }

    with open(SAVE_FILE, "w") as file:
        json.dump(game_state, file, indent=4)
'''

def save_game(profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds, player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards):
    """Save the current game state to the SQLite database."""
    from database import save_game as db_save_game  # Import from your database module
    db_save_game(profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds, 
                 player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards)

'''
for .json
def load_game():
    """Load the game state from a file."""
    if not Path(SAVE_FILE).exists():
        return None  # No save file found

    with open(SAVE_FILE, "r") as file:
        game_state = json.load(file)

    return game_state
'''

def load_game():
    """Load the latest game state from the SQLite database."""
    from database import load_game as db_load_game  # Import from your database module
    return db_load_game()  # Returns the latest game state


def show_peek(screen, player_deck, enemy_deck, cursor_pos, selected_pos):
    screen.fill(WHITE)
    y_offset = 50

    # Display player deck
    font = pygame.font.Font(UNICODE_FONT, 36)
    text = font.render("Your Deck (Next Cards):", True, GREEN)
    screen.blit(text, (50, y_offset))
    y_offset += 40

    small_font = pygame.font.Font(UNICODE_FONT, 24)
    for i, card in enumerate(player_deck):
        hovered = (i == cursor_pos)
        selected = (i == selected_pos)
        card_text = f"{i + 1}. {card['rank']} of {card['suit']}"
        text_color = BLUE if i == 0 else BLACK  # Highlight next card
        text = small_font.render(card_text, True, text_color)
        screen.blit(text, (50, y_offset))
        if hovered or selected:
            pygame.draw.rect(screen, YELLOW if hovered else CYAN, (45, y_offset - 5, 300, 25))
        y_offset += 30

    # Display enemy deck
    y_offset = 50
    text = font.render("Enemy Deck (Next Cards):", True, RED)
    screen.blit(text, (WIDTH // 2 + 50, y_offset))
    y_offset += 40

    for i, card in enumerate(enemy_deck):
        card_text = f"{i + 1}. {card['rank']} of {card['suit']}"
        text_color = BLUE if i == 0 else BLACK  # Highlight next card
        text = small_font.render(card_text, True, text_color)
        screen.blit(text, (WIDTH // 2 + 50, y_offset))
        y_offset += 30

    # Instructions
    text = small_font.render("Use UP/DOWN to move, ENTER to select/swap, 'P' to exit", True, BLACK)
    screen.blit(text, (10, HEIGHT - 50))

    pygame.display.flip()

def show_stats(screen, total_rounds, player_wins, enemy_wins, ties, player_deck, enemy_deck, cards_played, win_streak, longest_win_streak, played_cards, current_war, current_skirmish, player_advantage, enemy_advantage, score_to_beat):
    screen.fill(WHITE)
    y_offset = 50

    # Display stats
    stats = [
        f"Total Rounds: {total_rounds}",
        f"Player Wins: {player_wins}",
        f"Enemy Wins: {enemy_wins}",
        f"Ties: {ties}",
        f"Cards Remaining (Player): {len(player_deck)}",
        f"Cards Remaining (Enemy): {len(enemy_deck)}",
        f"Cards Played: {cards_played}",
        f"Current Win Streak: {win_streak}",
        f"Longest Win Streak: {longest_win_streak}",
        f"Most Common Card: {most_common_card(played_cards)}",
        f"Current War: {current_war}",
        f"Current Skirmish: {current_skirmish}",
        f"Player Advantage: {player_advantage}",
        f"Enemy Advantage: {enemy_advantage}",
        f"Score to Beat: {score_to_beat}"
    ]

    small_font = pygame.font.Font(UNICODE_FONT, 24)
    for stat in stats:
        text = small_font.render(stat, True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 30

    pygame.display.flip()

'''
for .json
def most_common_card(played_cards):
    if not played_cards:
        return "None"
    counter = Counter(played_cards)
    return counter.most_common(1)[0][0]
'''

def most_common_card(played_cards):
    if not played_cards:
        return "None"
    counter = Counter(played_cards)
    return counter.most_common(1)[0][0] if counter else "None"

def calculate_advantage(player_card, enemy_card):
    """Calculate advantage points based on card value and suit."""
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suit_order = {'♥': 4, '♦': 3, '♣': 2, '♠': 1}  # Hearts > Diamonds > Clubs > Spades

    # Calculate rank difference
    player_rank = rank_order.index(player_card['rank'])
    enemy_rank = rank_order.index(enemy_card['rank'])
    rank_difference = player_rank - enemy_rank

    # Calculate suit advantage
    player_suit = suit_order.get(player_card['suit'], 0)
    enemy_suit = suit_order.get(enemy_card['suit'], 0)
    suit_advantage = player_suit - enemy_suit

    # Total advantage points
    advantage_points = (rank_difference * 2) + suit_advantage  # Adjust weights as needed
    return advantage_points

def calculate_score_to_beat(war_number):
    """Calculate the score to beat based on the war number."""
    base_score = 10  # Starting score
    exponential_factor = 1.5  # Multiplier for exponential growth
    if war_number <= 4:
        return base_score * war_number  # Linear growth for the first 4 wars
    else:
        return int(base_score * (exponential_factor ** (war_number - 1)))  # Exponential growth after the 4th war


def main_game_loop(profile_id, loaded_state=None):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("War Game - Card Swapping Edition")

    # Initialize game state
    if loaded_state:
        player_deck = loaded_state["player_deck"]
        enemy_deck = loaded_state["enemy_deck"]
        player_score = loaded_state["player_score"]
        enemy_score = loaded_state["enemy_score"]
        total_rounds = loaded_state["total_rounds"]
        player_wins = loaded_state["player_wins"]
        enemy_wins = loaded_state["enemy_wins"]
        ties = loaded_state["ties"]
        cards_played = loaded_state["cards_played"]
        win_streak = loaded_state["win_streak"]
        longest_win_streak = loaded_state["longest_win_streak"]
        played_cards = loaded_state["played_cards"]
        current_war = loaded_state["current_war"]
        current_skirmish = loaded_state["current_skirmish"]
        player_advantage = loaded_state["player_advantage"]
        enemy_advantage = loaded_state["enemy_advantage"]
    else:
        deck = create_deck()
        shuffle_deck(deck)
        player_deck, enemy_deck = split_deck(deck)

        player_discard = []
        enemy_discard = []

        player_score = 0
        enemy_score = 0

        total_rounds = 0
        player_wins = 0
        enemy_wins = 0
        ties = 0
        cards_played = 0
        win_streak = 0
        longest_win_streak = 0
        played_cards = []

        current_war = 1
        current_skirmish = 1
        player_advantage = 0
        enemy_advantage = 0

    # Calculate the score to beat for the current war
    score_to_beat = calculate_score_to_beat(current_war)

    cursor_pos = 0
    selected_pos = None

    running = True
    peek_mode = False
    stats_mode = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if peek_mode:
                    if event.key == pygame.K_UP:
                        cursor_pos = max(0, cursor_pos - 1)
                    elif event.key == pygame.K_DOWN:
                        cursor_pos = min(len(player_deck) - 1, cursor_pos + 1)
                    elif event.key == pygame.K_RETURN:
                        if selected_pos is None:
                            selected_pos = cursor_pos
                        else:
                            player_deck[selected_pos], player_deck[cursor_pos] = (
                                player_deck[cursor_pos], player_deck[selected_pos]
                            )
                            selected_pos = None
                    elif event.key == pygame.K_p:
                        peek_mode = False
                        selected_pos = None
                else:
                    if event.key == pygame.K_p:
                        peek_mode = not peek_mode
                        stats_mode = False
                    elif event.key == pygame.K_s:
                        stats_mode = not stats_mode
                        peek_mode = False
                    elif event.key == pygame.K_SPACE:
                        if player_deck and enemy_deck:
                            player_card = player_deck.pop(0)
                            enemy_card = enemy_deck.pop(0)

                            played_cards.append(player_card['rank'])
                            played_cards.append(enemy_card['rank'])
                            cards_played += 2

                            # Calculate advantage points
                            player_advantage += calculate_advantage(player_card, enemy_card)
                            enemy_advantage += calculate_advantage(enemy_card, player_card)

                            # Display skirmish result
                            print(f"Skirmish {current_skirmish} of War {current_war}:")
                            print(f"Player Advantage: {player_advantage}")
                            print(f"Enemy Advantage: {enemy_advantage}")
                            print(f"Score to Beat: {score_to_beat}")

                            # Move cards to discard piles
                            player_discard.append(player_card)
                            enemy_discard.append(enemy_card)

                            # Check if skirmish is over
                            if current_skirmish == 3:
                                # Determine war winner
                                if player_advantage >= score_to_beat:
                                    outcome = "You win this war!"
                                    player_score += 1
                                    player_wins += 1
                                    win_streak += 1
                                    if win_streak > longest_win_streak:
                                        longest_win_streak = win_streak
                                else:
                                    outcome = "Enemy wins this war!"
                                    enemy_score += 1
                                    enemy_wins += 1
                                    win_streak = 0

                                # Reset for the next war
                                current_war += 1
                                current_skirmish = 1
                                player_advantage = 0
                                enemy_advantage = 0
                                score_to_beat = calculate_score_to_beat(current_war)
                            else:
                                current_skirmish += 1

                            total_rounds += 1

                            # Check if all cards are played
                            if not player_deck and not enemy_deck:
                                running = False
                    elif event.key == pygame.K_F5:  # Save game
                        save_game(profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds, 
                                  player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards,
                                  current_war, current_skirmish, player_advantage, enemy_advantage)
                        print("Game saved!")
                    elif event.key == pygame.K_ESCAPE:  # Return to main menu
                        running = False

        screen.fill(WHITE)

        # Display scores
        font = pygame.font.Font(UNICODE_FONT, 36)
        text = font.render(f"Player Score: {player_score}", True, BLACK)
        screen.blit(text, (50, 50))
        text = font.render(f"Enemy Score: {enemy_score}", True, BLACK)
        screen.blit(text, (WIDTH - 250, 50))

        # Display cards if available
        if player_deck and enemy_deck:
            draw_card(screen, 150, 200, player_deck[0], is_player=True)
            draw_card(screen, 450, 200, enemy_deck[0], is_player=False)

        # Display war and skirmish info
        war_info = f"War {current_war} - Skirmish {current_skirmish}"
        text = font.render(war_info, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150))

        # Display advantage points and score to beat
        advantage_info = f"Player Advantage: {player_advantage} / {score_to_beat}"
        text = font.render(advantage_info, True, GREEN if player_advantage >= score_to_beat else RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))

        # Display peek mode or stats mode
        if peek_mode:
            show_peek(screen, player_deck, enemy_deck, cursor_pos, selected_pos)
        elif stats_mode:
            show_stats(screen, total_rounds, player_wins, enemy_wins, ties, player_deck, enemy_deck, cards_played, win_streak, longest_win_streak, played_cards, current_war, current_skirmish, player_advantage, enemy_advantage, score_to_beat)
        else:
            small_font = pygame.font.Font(UNICODE_FONT, 24)
            text = small_font.render("Press 'P' to peek at both decks", True, BLACK)
            screen.blit(text, (10, HEIGHT - 50))
            text = small_font.render("Press 'S' to view stats", True, BLACK)
            screen.blit(text, (10, HEIGHT - 80))
            text = small_font.render("Press SPACE to draw cards", True, BLACK)
            screen.blit(text, (10, HEIGHT - 110))
            text = small_font.render("Press F5 to save, ESC to return to menu", True, BLACK)
            screen.blit(text, (10, HEIGHT - 140))

        pygame.display.flip()

    # Determine the winner
    screen.fill(WHITE)
    if player_score > enemy_score:
        text = font.render("You won the game! You have the most points.", True, GREEN)
    elif player_score < enemy_score:
        text = font.render("You lost the game! The enemy has the most points.", True, RED)
    else:
        text = font.render("It's a tie! Both players have the same points.", True, BLACK)
    screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))
    pygame.display.flip()

    # Wait before closing
    pygame.time.delay(3000)
    pygame.quit()