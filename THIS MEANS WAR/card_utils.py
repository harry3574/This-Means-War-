from constants import RED, BLACK, WHITE, YELLOW, CYAN
import pygame

def draw_card(screen, x, y, card, is_player=True, hovered=False, selected=False):
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
    font = pygame.font.Font(None, 36)
    text = font.render(rank, True, color)
    screen.blit(text, (x + 10, y + 10))
    text = font.render(suit, True, color)
    screen.blit(text, (x + 10, y + 40))

    # Label for player/enemy
    label = "Player" if is_player else "Enemy"
    small_font = pygame.font.Font(None, 24)
    text = small_font.render(label, True, BLACK)
    screen.blit(text, (x + 10, y + 130))

def compare_cards(card1, card2):
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return rank_order.index(card1['rank']) - rank_order.index(card2['rank'])