from dataclasses import dataclass, field
from typing import List

from constants import BASE_SCORE
from .deck import Card

@dataclass
class WarGameState:
    # Decks
    player_deck: List[Card] = field(default_factory=list)
    enemy_deck: List[Card] = field(default_factory=list)
    player_discard: List[Card] = field(default_factory=list)
    enemy_discard: List[Card] = field(default_factory=list)
    
    # Scores
    player_score: int = 0
    enemy_score: int = 0
    
    # Progress
    current_war: int = 1
    current_skirmish: int = 1
    current_hand: int = 1
    
    # Stats
    player_wins: int = 0
    enemy_wins: int = 0
    ties: int = 0
    win_streak: int = 0
    longest_win_streak: int = 0
    cards_played: int = 0
    played_cards: List[str] = field(default_factory=list)
    
    # Advantage
    player_advantage: int = 0
    enemy_advantage: int = 0
    
    @property
    def score_to_beat(self) -> int:
        if self.current_war <= 4:
            return BASE_SCORE * self.current_war
        return int(BASE_SCORE * (1.5 ** (self.current_war - 1)))