import random
from typing import List, Dict, Tuple
from constants import SUITS, RANKS, SEED

def create_deck() -> List[Dict[str, str]]:
    """
    Create a standard 52-card deck
    Returns:
        List of card dictionaries with 'rank' and 'suit' keys
    """
    return [{'rank': rank, 'suit': suit} for suit in SUITS for rank in RANKS]

def shuffle_deck(deck: List[Dict[str, str]]) -> None:
    """
    Shuffle the deck in place using the game seed
    Args:
        deck: List of cards to shuffle
    """
    random.seed(SEED)
    random.shuffle(deck)

def split_deck(deck: List[Dict[str, str]]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Split the deck into two equal halves
    Args:
        deck: Complete deck to split
    Returns:
        Tuple of (player_deck, enemy_deck)
    """
    return deck[:26], deck[26:]

def compare_cards(card1: Dict[str, str], card2: Dict[str, str]) -> int:
    """
    Compare two cards' ranks
    Args:
        card1: First card to compare
        card2: Second card to compare
    Returns:
        Positive if card1 > card2, negative if card2 > card1, 0 if equal
    """
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    rank1 = rank_order.index(card1['rank'])
    rank2 = rank_order.index(card2['rank'])
    return rank1 - rank2

def calculate_advantage(player_card: Dict[str, str], enemy_card: Dict[str, str]) -> int:
    """
    Calculate advantage points between two cards
    Args:
        player_card: Player's card
        enemy_card: Enemy's card
    Returns:
        Advantage points (positive favors player, negative favors enemy)
    """
    rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suit_order = {'♥': 4, '♦': 3, '♣': 2, '♠': 1}  # Hearts > Diamonds > Clubs > Spades

    player_rank = rank_order.index(player_card['rank'])
    enemy_rank = rank_order.index(enemy_card['rank'])
    rank_diff = player_rank - enemy_rank

    player_suit = suit_order.get(player_card['suit'], 0)
    enemy_suit = suit_order.get(enemy_card['suit'], 0)
    suit_diff = player_suit - enemy_suit

    return (rank_diff * 2) + suit_diff