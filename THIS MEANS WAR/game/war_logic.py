import random
from typing import List
from .deck import Card
from .game_state import WarGameState
from constants import HANDS_PER_SKIRMISH, SKIRMISHES_PER_WAR

class WarLogic:
    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)
        
    def shuffle_deck(self, deck: List[Card]) -> List[Card]:
        """Deterministic shuffle based on seed"""
        self.rng.shuffle(deck)
        return deck

    @staticmethod
    def calculate_advantage(player_card: Card, enemy_card: Card) -> int:
        """Static method as before (no changes needed)"""
        suit_values = {'♥': 4, '♦': 3, '♣': 2, '♠': 1}
        rank_diff = player_card.value - enemy_card.value
        suit_diff = suit_values[player_card.suit] - suit_values[enemy_card.suit]
        return (rank_diff * 2) + suit_diff

    def resolve_hand(self, state: WarGameState) -> str:
        """Deterministic hand resolution"""
        if not state.player_deck or not state.enemy_deck:
            return "game_over"
            
        # Cards are drawn in predetermined order
        player_card = state.player_deck.pop(0)
        enemy_card = state.enemy_deck.pop(0)
        
        # Rest of the logic remains the same...
        state.cards_played += 2
        state.played_cards.extend([player_card.rank, enemy_card.rank])
        
        advantage = self.calculate_advantage(player_card, enemy_card)
        state.player_advantage += advantage
        state.enemy_advantage -= advantage
        
        state.player_discard.append(player_card)
        state.enemy_discard.append(enemy_card)
        
        state.current_hand += 1
        if state.current_hand > HANDS_PER_SKIRMISH:
            return self.resolve_skirmish(state)
            
        return "continue"

    def resolve_skirmish(self, state: WarGameState) -> str:
        """Skirmish resolution with deterministic reshuffle"""
        if state.player_advantage >= state.score_to_beat:
            state.player_wins += 1
            state.win_streak += 1
            if state.win_streak > state.longest_win_streak:
                state.longest_win_streak = state.win_streak
            outcome = "player_win"
        else:
            state.enemy_wins += 1
            state.win_streak = 0
            outcome = "enemy_win"
        
        # Deterministic reshuffle
        combined = state.player_discard + state.enemy_discard
        state.player_deck = self.shuffle_deck(combined[:len(combined)//2])
        state.enemy_deck = self.shuffle_deck(combined[len(combined)//2:])
        
        # Reset state
        state.player_discard = []
        state.enemy_discard = []
        state.player_advantage = 0
        state.enemy_advantage = 0
        state.current_hand = 1
        
        state.current_skirmish += 1
        if state.current_skirmish > SKIRMISHES_PER_WAR:
            return self.resolve_war(state, outcome)
            
        return "skirmish_complete"

    def resolve_war(self, state: WarGameState, outcome: str) -> str:
        """War resolution (no changes needed)"""
        if state.player_wins > state.enemy_wins:
            state.player_score += 1
        elif state.player_wins < state.enemy_wins:
            state.enemy_score += 1
        else:
            state.ties += 1
        
        state.current_war += 1
        state.current_skirmish = 1
        state.player_wins = 0
        state.enemy_wins = 0
        
        return "war_complete"