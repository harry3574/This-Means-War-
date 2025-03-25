# game/state.py
from dataclasses import dataclass
from .logic import GameLogic

@dataclass
class GameState:
    """Container for all game state variables"""
    player_deck: list
    enemy_deck: list
    player_score: int = 0
    enemy_score: int = 0
    total_rounds: int = 0
    player_wins: int = 0
    enemy_wins: int = 0
    ties: int = 0
    cards_played: int = 0
    win_streak: int = 0
    longest_win_streak: int = 0
    played_cards: list = None
    current_war: int = 1
    current_skirmish: int = 1
    current_hand: int = 1
    player_advantage: int = 0
    enemy_advantage: int = 0
    
    def __post_init__(self):
        if self.played_cards is None:
            self.played_cards = []
        
        self.score_to_beat = self.calculate_score_to_beat(self.current_war)
    
    @staticmethod
    def calculate_score_to_beat(war_number):
        return GameLogic.calculate_score_to_beat(war_number)