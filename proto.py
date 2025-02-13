import random
import pygame
import sys
from collections import Counter

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("War Game - Card Swapping Edition")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Fonts
font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Define the deck
suits = ['♥', '♦', '♣', '♠']  # Hearts, Diamonds, Clubs, Spades
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

# Seed for reproducibility
seed = 42  # Default seed
random.seed(seed)

# Shuffle the deck
random.shuffle(deck)

# Split the deck into two equal halves
player_deck = deck[:26]
enemy_deck = deck[26:]

# Discard piles
player_discard = []
enemy_discard = []

# Scores
player_score = 0
enemy_score = 0

# Stats trackers
total_rounds = 0
player_wins = 0
enemy_wins = 0
ties = 0
cards_played = 0
win_streak = 0
longest_win_streak = 0
played_cards = []  # Track all cards played for stats

# Card-swapping variables
cursor_pos = 0  # Current position of the cursor
selected_pos = None  # Position of the selected card (if any)

# Function to display a card
def draw_card(x, y, card, is_player=True, hovered=False, selected=False):
    color = RED if card['suit'] in ['♥', '♦'] else BLACK
    rank = card['rank']
    suit = card['suit']

    # Draw card background
    if hovered:
        pygame.draw.rect(screen, YELLOW, (x, y, 100, 150))
    elif selected:
        pygame.draw.rect(screen, CYAN, (x, y, 100, 150))
    else:
        pygame.draw.rect(screen, WHITE, (x, y, 100, 150))
    pygame.draw.rect(screen, BLACK, (x, y, 100, 150), 2)

    # Render rank and suit
    text = font.render(rank, True, color)
    screen.blit(text, (x + 10, y + 10))
    text = font.render(suit, True, color)
    screen.blit(text, (x + 10, y + 40))

    # Label for player/enemy
    label = "Player" if is_player else "Enemy"
    text = small_font.render(label, True, BLACK)
    screen.blit(text, (x + 10, y + 130))

# Function to display both decks in list form (peek mode)
def show_peek():
    screen.fill(WHITE)
    y_offset = 50

    # Display player deck
    text = font.render("Your Deck (Next Cards):", True, GREEN)
    screen.blit(text, (50, y_offset))
    y_offset += 40

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

# Function to compare two cards and determine the winner
def compare_cards(card1, card2):
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return rank_order.index(card1['rank']) - rank_order.index(card2['rank'])

# Function to display stats
def show_stats():
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
        f"Most Common Card: {most_common_card()}"
    ]

    for stat in stats:
        text = small_font.render(stat, True, BLACK)
        screen.blit(text, (50, y_offset))
        y_offset += 30

    pygame.display.flip()

# Function to calculate the most common card played
def most_common_card():
    if not played_cards:
        return "None"
    counter = Counter(played_cards)
    return counter.most_common(1)[0][0]

# Main game loop
round_number = 1
running = True
peek_mode = False
stats_mode = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if peek_mode:
                if event.key == pygame.K_UP:  # Move cursor up
                    cursor_pos = max(0, cursor_pos - 1)
                elif event.key == pygame.K_DOWN:  # Move cursor down
                    cursor_pos = min(len(player_deck) - 1, cursor_pos + 1)
                elif event.key == pygame.K_RETURN:  # Select/swap cards
                    if selected_pos is None:
                        selected_pos = cursor_pos  # Select the card
                    else:
                        # Swap the selected card with the current cursor position
                        player_deck[selected_pos], player_deck[cursor_pos] = (
                            player_deck[cursor_pos], player_deck[selected_pos]
                        )
                        selected_pos = None  # Reset selection
                elif event.key == pygame.K_p:  # Exit peek mode
                    peek_mode = False
                    selected_pos = None  # Reset selection
            else:
                if event.key == pygame.K_p:  # Toggle peek mode
                    peek_mode = not peek_mode
                    stats_mode = False
                elif event.key == pygame.K_s:  # Toggle stats mode
                    stats_mode = not stats_mode
                    peek_mode = False
                elif event.key == pygame.K_SPACE:  # Draw cards
                    if player_deck and enemy_deck:
                        # Draw cards
                        player_card = player_deck.pop(0)
                        enemy_card = enemy_deck.pop(0)

                        # Track cards played
                        played_cards.append(player_card['rank'])
                        played_cards.append(enemy_card['rank'])
                        cards_played += 2

                        # Compare cards
                        result = compare_cards(player_card, enemy_card)
                        if result > 0:
                            outcome = "You win this round!"
                            player_score += 1
                            player_wins += 1
                            win_streak += 1
                            if win_streak > longest_win_streak:
                                longest_win_streak = win_streak
                        elif result < 0:
                            outcome = "Enemy wins this round!"
                            enemy_score += 1
                            enemy_wins += 1
                            win_streak = 0
                        else:
                            outcome = "It's a tie! No points awarded."
                            ties += 1

                        # Move cards to discard piles
                        player_discard.append(player_card)
                        enemy_discard.append(enemy_card)

                        # Increment round counter
                        total_rounds += 1

                        # Check if all cards are played
                        if not player_deck and not enemy_deck:
                            running = False

    screen.fill(WHITE)

    # Display scores
    text = font.render(f"Player Score: {player_score}", True, BLACK)
    screen.blit(text, (50, 50))
    text = font.render(f"Enemy Score: {enemy_score}", True, BLACK)
    screen.blit(text, (WIDTH - 250, 50))

    # Display cards if available
    if player_deck and enemy_deck:
        draw_card(150, 200, player_deck[0], is_player=True)
        draw_card(450, 200, enemy_deck[0], is_player=False)

    # Display peek mode or stats mode
    if peek_mode:
        show_peek()
    elif stats_mode:
        show_stats()
    else:
        text = small_font.render("Press 'P' to peek at both decks", True, BLACK)
        screen.blit(text, (10, HEIGHT - 50))
        text = small_font.render("Press 'S' to view stats", True, BLACK)
        screen.blit(text, (10, HEIGHT - 80))
        text = small_font.render("Press SPACE to draw cards", True, BLACK)
        screen.blit(text, (10, HEIGHT - 110))

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
sys.exit()