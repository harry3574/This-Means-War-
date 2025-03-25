# game/logic.py
from collections import Counter
from .deck import compare_cards, calculate_advantage

class GameLogic:
    @staticmethod
    def calculate_score_to_beat(war_number):
        """Calculate the score needed to win a skirmish"""
        base_score = 10
        exponential_factor = 1.5
        
        if war_number <= 4:
            return base_score * war_number
        return int(base_score * (exponential_factor ** (war_number - 1)))

    @staticmethod
    def play_hand(player_card, enemy_card, game_state):
        """Process a single hand and update game state"""
        # Calculate advantage
        advantage = GameLogic.calculate_advantage(player_card, enemy_card)
        game_state.player_advantage += advantage
        game_state.enemy_advantage -= advantage
        
        # Update played cards
        game_state.played_cards.extend([player_card['rank'], enemy_card['rank']])
        game_state.cards_played += 2
        game_state.current_hand += 1
        game_state.total_rounds += 1
        
        # Check skirmish completion (26 hands)
        if game_state.current_hand > 26:
            GameLogic.complete_skirmish(game_state)
            
        return compare_cards(player_card, enemy_card)

    @staticmethod
    def complete_skirmish(game_state):
        """Handle skirmish completion"""
        if game_state.player_advantage >= game_state.score_to_beat:
            game_state.player_wins += 1
            game_state.win_streak += 1
            if game_state.win_streak > game_state.longest_win_streak:
                game_state.longest_win_streak = game_state.win_streak
        else:
            game_state.enemy_wins += 1
            game_state.win_streak = 0
        
        # Check war completion (3 skirmishes)
        if game_state.current_skirmish >= 3:
            GameLogic.complete_war(game_state)
        else:
            game_state.current_skirmish += 1
        
        # Reset for next skirmish
        game_state.current_hand = 1
        game_state.player_advantage = 0
        game_state.enemy_advantage = 0
        game_state.score_to_beat = GameLogic.calculate_score_to_beat(game_state.current_war)

    @staticmethod
    def complete_war(game_state):
        """Handle war completion"""
        if game_state.player_wins > game_state.enemy_wins:
            game_state.player_score += 1
        elif game_state.enemy_wins > game_state.player_wins:
            game_state.enemy_score += 1
        else:
            game_state.ties += 1
        
        # Reset for next war
        game_state.current_war += 1
        game_state.current_skirmish = 1
        game_state.player_wins = 0
        game_state.enemy_wins = 0