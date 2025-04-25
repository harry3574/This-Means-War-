class Card:
    def __init__(self, suit: str, value: str):
        self.suit = suit
        self.value = value
        self.rank = self._get_rank()

    SUIT_ADVANTAGES = {
        '♠': {'♥': 1.5, '♦': 0.5, '♣': 1.0},  # Spades
        '♥': {'♦': 1.5, '♣': 0.5, '♠': 1.0},  # Hearts
        '♦': {'♣': 1.5, '♠': 0.5, '♥': 1.0},  # Diamonds
        '♣': {'♠': 1.5, '♥': 0.5, '♦': 1.0}   # Clubs
    }

    def _get_rank(self) -> int:
        """Convert card value to numerical rank for comparison"""
        values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                  '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                  'K': 13, 'A': 14}
        return values[self.value]
    
    def get_suit_advantage(self, other_suit: str) -> float:
        """Returns the multiplier based on suit advantage"""
        return self.SUIT_ADVANTAGES[self.suit].get(other_suit, 1.0)
    
    def __repr__(self):
        return f"{self.value}{self.suit}"