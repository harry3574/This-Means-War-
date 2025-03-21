import random
import pygame
from collections import Counter
from constants import WIDTH, HEIGHT, SEED, WHITE, BLACK, GREEN, RED, BLUE, YELLOW, CYAN, UNICODE_FONT
from deck import create_deck, shuffle_deck, split_deck
from card_utils import draw_card, compare_cards
import json
from pathlib import Path
from database import save_game, load_game
from tts_handler import TTSHandler

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

def show_peek(screen, player_deck, enemy_deck, cursor_pos, selected_pos, scroll_offset):
    screen.fill(WHITE)
    y_offset = 50
    card_width = 100  # Width of each card column
    card_height = 150  # Height of each card
    spacing = 20  # Spacing between cards
    visible_cards = WIDTH // (card_width + spacing)  # Number of cards visible on screen

    # Pastel colors for hovered and selected cards
    PASTEL_YELLOW = (255, 255, 153)  # Light pastel yellow for hovered player cards
    PASTEL_CYAN = (153, 255, 255)    # Light pastel cyan for selected player cards
    PASTEL_RED = (255, 153, 153)     # Light pastel red for enemy cards facing the hovered player card

    # Helper function to draw a card with a background rectangle
    def draw_card_peek(screen, card, x, y, is_player=True, hovered=False, selected=False, enemy_hovered=False):
        # Draw background rectangle for hovered or selected cards
        if hovered:
            pygame.draw.rect(screen, PASTEL_YELLOW, (x - 5, y - 5, card_width + 10, card_height + 10))
        elif selected:
            pygame.draw.rect(screen, PASTEL_CYAN, (x - 5, y - 5, card_width + 10, card_height + 10))
        elif enemy_hovered:
            pygame.draw.rect(screen, PASTEL_RED, (x - 5, y - 5, card_width + 10, card_height + 10))

        # Draw card background
        pygame.draw.rect(screen, WHITE, (x, y, card_width, card_height))
        pygame.draw.rect(screen, BLACK, (x, y, card_width, card_height), 2)

        # Render rank and suit
        color = RED if card['suit'] in ['♥', '♦'] else BLACK
        rank = card['rank']
        suit = card['suit']

        font = pygame.font.Font(None, 24)
        text = font.render(rank, True, color)
        screen.blit(text, (x + 10, y + 10))
        text = font.render(suit, True, color)
        screen.blit(text, (x + 10, y + 40))

    # Draw enemy deck (now at the top)
    font = pygame.font.Font(UNICODE_FONT, 36)
    text = font.render("Enemy Deck (Next Cards):", True, RED)
    screen.blit(text, (50, y_offset))
    y_offset += 40

    for i in range(scroll_offset, min(len(enemy_deck), scroll_offset + visible_cards)):
        card = enemy_deck[i]
        x = 50 + (i - scroll_offset) * (card_width + spacing)
        # Highlight the enemy card if the player is hovering over the corresponding card
        enemy_hovered = (i == cursor_pos)
        draw_card_peek(screen, card, x, y_offset, is_player=False, enemy_hovered=enemy_hovered)

    # Draw advantage points between the decks
    y_offset += card_height + 10  # Space between enemy deck and advantage points
    small_font = pygame.font.Font(UNICODE_FONT, 24)
    for i in range(scroll_offset, min(len(player_deck), scroll_offset + visible_cards)):
        player_card = player_deck[i]
        enemy_card = enemy_deck[i]
        advantage = calculate_advantage(player_card, enemy_card)
        advantage_text = f"{'+' if advantage >= 0 else ''}{advantage}"
        advantage_color = GREEN if advantage >= 0 else RED
        x = 50 + (i - scroll_offset) * (card_width + spacing) + card_width // 2 - 10
        text = small_font.render(advantage_text, True, advantage_color)
        screen.blit(text, (x, y_offset))

    # Draw player deck (now at the bottom)
    y_offset += 30  # Space between advantage points and player deck
    text = font.render("Your Deck (Next Cards):", True, GREEN)
    screen.blit(text, (50, y_offset))
    y_offset += 40

    for i in range(scroll_offset, min(len(player_deck), scroll_offset + visible_cards)):
        card = player_deck[i]
        x = 50 + (i - scroll_offset) * (card_width + spacing)
        draw_card_peek(screen, card, x, y_offset, is_player=True, hovered=(i == cursor_pos), selected=(i == selected_pos))

    # Draw up/down arrows for direct confrontations
    arrow_font = pygame.font.Font(None, 36)
    for i in range(scroll_offset, min(len(player_deck), scroll_offset + visible_cards)):
        x = 50 + (i - scroll_offset) * (card_width + spacing) + card_width // 2 - 10
        y = y_offset + card_height + 10
        text = arrow_font.render("↑↓", True, BLACK)
        screen.blit(text, (x, y))

    # Draw scroll indicators
    if scroll_offset > 0:
        text = font.render("<", True, BLACK)
        screen.blit(text, (10, HEIGHT // 2 - 20))
    if scroll_offset + visible_cards < len(player_deck):
        text = font.render(">", True, BLACK)
        screen.blit(text, (WIDTH - 40, HEIGHT // 2 - 20))

    # Instructions
    small_font = pygame.font.Font(UNICODE_FONT, 24)
    instructions = [
        "Use LEFT/RIGHT to scroll, UP/DOWN to move, ENTER to select/swap, 'P' to exit",
        "Selected card will be highlighted in CYAN"
    ]
    for i, line in enumerate(instructions):
        text = small_font.render(line, True, BLACK)
        screen.blit(text, (10, HEIGHT - 50 - i * 30))

    pygame.display.flip()

    # Instructions
    small_font = pygame.font.Font(UNICODE_FONT, 24)
    instructions = [
        "Use LEFT/RIGHT to scroll, UP/DOWN to move, ENTER to select/swap, 'P' to exit",
        "Selected card will be highlighted in CYAN"
    ]
    for i, line in enumerate(instructions):
        text = small_font.render(line, True, BLACK)
        screen.blit(text, (10, HEIGHT - 50 - i * 30))

    pygame.display.flip()


def show_stats(screen, total_rounds, player_wins, enemy_wins, ties, player_deck, enemy_deck, cards_played, win_streak, longest_win_streak, played_cards, current_war, current_skirmish, current_hand, player_advantage, enemy_advantage, score_to_beat):
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
        f"Current Hand: {current_hand}",
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

    # Initialize TTS handler
    tts = TTSHandler(rate=150, volume=1.0)

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
        current_hand = loaded_state["current_hand"]
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
        current_hand = 1
        player_advantage = 0
        enemy_advantage = 0

    # Calculate the score to beat for the current skirmish
    score_to_beat = calculate_score_to_beat(current_war)

    cursor_pos = 0
    selected_pos = None
    scroll_offset = 0  # Initialize scroll offset

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
                    elif event.key == pygame.K_LEFT:
                        # Move cursor left and scroll if necessary
                        if cursor_pos > 0:
                            cursor_pos -= 1
                            # Scroll if cursor moves out of the visible range
                            if cursor_pos < scroll_offset:
                                scroll_offset = max(0, cursor_pos)
                    elif event.key == pygame.K_RIGHT:
                        # Move cursor right and scroll if necessary
                        if cursor_pos < len(player_deck) - 1:
                            cursor_pos += 1
                            # Scroll if cursor moves out of the visible range
                            visible_cards = WIDTH // (100 + 20)  # Card width + spacing
                            if cursor_pos >= scroll_offset + visible_cards:
                                scroll_offset = min(len(player_deck) - visible_cards, cursor_pos - visible_cards + 1)
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

                            # Display hand result
                            print(f"War {current_war} - Skirmish {current_skirmish} - Hand {current_hand}:")
                            print(f"Player Advantage: {player_advantage}")
                            print(f"Enemy Advantage: {enemy_advantage}")
                            print(f"Score to Beat: {score_to_beat}")

                            # Move cards to discard piles
                            player_discard.append(player_card)
                            enemy_discard.append(enemy_card)

                            # Check if skirmish is over (26 hands)
                            if current_hand == 26:
                                # Determine skirmish winner
                                if player_advantage >= score_to_beat:
                                    outcome = "You win this skirmish!"
                                    player_wins += 1
                                    win_streak += 1
                                    if win_streak > longest_win_streak:
                                        longest_win_streak = win_streak
                                else:
                                    outcome = "Enemy wins this skirmish!"
                                    enemy_wins += 1
                                    win_streak = 0

                                # Reset decks for the next skirmish
                                combined_deck = player_discard + enemy_discard
                                shuffle_deck(combined_deck)  # Shuffle using the current seed
                                player_deck, enemy_deck = split_deck(combined_deck)  # Split into two decks
                                player_discard = []
                                enemy_discard = []

                                # Check if war is over (3 skirmishes)
                                if current_skirmish == 3:
                                    # Determine war winner
                                    if player_wins > enemy_wins:
                                        player_score += 1
                                    elif player_wins < enemy_wins:
                                        enemy_score += 1
                                    else:
                                        ties += 1

                                    # Reset for the next war
                                    current_war += 1
                                    current_skirmish = 1
                                    player_wins = 0
                                    enemy_wins = 0
                                else:
                                    # Reset for the next skirmish
                                    current_skirmish += 1

                                # Reset for the next skirmish
                                current_hand = 1
                                player_advantage = 0
                                enemy_advantage = 0
                                score_to_beat = calculate_score_to_beat(current_war)
                            else:
                                current_hand += 1

                            total_rounds += 1

                            # Check if all cards are played and no more wars are left
                            if not player_deck and not enemy_deck and current_war > 3:  # Adjust the war limit as needed
                                running = False
                    elif event.key == pygame.K_F3:  # Trigger TTS
                        if peek_mode:
                            tts_text = f"Peek mode. Your deck has {len(player_deck)} cards. Enemy deck has {len(enemy_deck)} cards."
                        elif stats_mode:
                            tts_text = f"Stats mode. Player score: {player_score}. Enemy score: {enemy_score}. Current war: {current_war}. Current skirmish: {current_skirmish}. Current hand: {current_hand}."
                        else:
                            # Get the current cards
                            player_card = player_deck[0] if player_deck else None
                            enemy_card = enemy_deck[0] if enemy_deck else None

                            # Build the TTS message
                            tts_text = f"Main game. Player score: {player_score}. Enemy score: {enemy_score}. "
                            tts_text += f"Current war: {current_war}. Current skirmish: {current_skirmish}. Current hand: {current_hand}. "
                            tts_text += f"Player advantage: {player_advantage}. Score to beat: {score_to_beat}. "
                            if player_card:
                                tts_text += f"Your card: {player_card['rank']} of {player_card['suit']}. "
                            if enemy_card:
                                tts_text += f"Enemy card: {enemy_card['rank']} of {enemy_card['suit']}."
                        tts.speak(tts_text)
                    elif event.key == pygame.K_F5:  # Save game
                        save_game(profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds, 
                                  player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards,
                                  current_war, current_skirmish, current_hand, player_advantage, enemy_advantage)
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
            player_card = player_deck[0]
            enemy_card = enemy_deck[0]
            draw_card(screen, 150, 200, player_card, is_player=True)
            draw_card(screen, 450, 200, enemy_card, is_player=False)

        # Display war, skirmish, and hand info
        war_info = f"War {current_war} - Skirmish {current_skirmish} - Hand {current_hand}"
        text = font.render(war_info, True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 150))

        # Display advantage points and score to beat
        advantage_info = f"Player Advantage: {player_advantage} / {score_to_beat}"
        text = font.render(advantage_info, True, GREEN if player_advantage >= score_to_beat else RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))

        # Display TTS instructions
        small_font = pygame.font.Font(UNICODE_FONT, 24)
        tts_instructions = "Press F3 for Text-to-Speech"
        text = small_font.render(tts_instructions, True, BLACK)
        screen.blit(text, (10, HEIGHT - 170))

        # Display peek mode or stats mode
        if peek_mode:
            show_peek(screen, player_deck, enemy_deck, cursor_pos, selected_pos, scroll_offset)
        elif stats_mode:
            show_stats(screen, total_rounds, player_wins, enemy_wins, ties, player_deck, enemy_deck, cards_played, win_streak, longest_win_streak, played_cards, current_war, current_skirmish, current_hand, player_advantage, enemy_advantage, score_to_beat)
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