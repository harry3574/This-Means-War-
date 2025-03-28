from dataclasses import dataclass, field
from typing import List, Optional
from .deck import Card

@dataclass
class Player:
    deck: List[Card]
    discard_pile: List[Card] = field(default_factory=list)
    cheat_points: int = 3  # Limited cheat attempts
    
    def play_card(self) -> Optional[Card]:
        if not self.deck:
            self.reshuffle_discard()
            if not self.deck:
                return None
        return self.deck.pop(0)
    
    def reshuffle_discard(self):
        """Shuffle discard pile back into deck (uses existing RNG)"""
        self.deck.extend(self.discard_pile)
        self.discard_pile.clear()
    
    def cheat_reorder(self, new_order: List[int]) -> bool:
        """Attempt to reorder deck, consuming cheat points"""
        if self.cheat_points <= 0:
            return False
            
        if len(new_order) != len(self.deck):
            return False
            
        try:
            self.deck = [self.deck[i] for i in new_order]
            self.cheat_points -= 1
            return True
        except IndexError:
            return False