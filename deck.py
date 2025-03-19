import random
from constants import SUITS, RANKS, SEED

def create_deck():
    return [{'rank': rank, 'suit': suit} for suit in SUITS for rank in RANKS]

def shuffle_deck(deck):
    random.seed(SEED)
    random.shuffle(deck)

def split_deck(deck):
    return deck[:26], deck[26:]