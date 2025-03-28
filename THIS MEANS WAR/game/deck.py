import random
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Card:
    rank: str
    suit: str
    value: int

class Deck:
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♥', '♦', '♣', '♠']
    
    def __init__(self, seed: Optional[int] = None):
        self.cards = [
            Card(rank=rank, suit=suit, value=idx) 
            for idx, rank in enumerate(self.RANKS, 2) 
            for suit in self.SUITS
        ]
        self.rng = random.Random(seed)
    
    def shuffle(self):
        self.rng.shuffle(self.cards)
    
    def split(self) -> tuple[List[Card], List[Card]]:
        half = len(self.cards) // 2
        return self.cards[:half], self.cards[half:]