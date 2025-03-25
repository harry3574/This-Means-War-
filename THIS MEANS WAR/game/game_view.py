# game/game_view.py
import arcade
from arcade import View, SpriteList
from views.game_over_view import GameOverView
from game.deck import create_deck, shuffle_deck, split_deck
from game.logic import GameLogic
from game.state import GameState
from game.tts import TTSHandler
from utils.database import save_game

class GameView(View):
    def __init__(self, profile_id=None, loaded_state=None):
        super().__init__()
        self.profile_id = profile_id
        self.state = self.initialize_state(loaded_state)
        self.card_sprites = SpriteList()
        self.ui_elements = SpriteList()
        self.tts = TTSHandler()
        self.setup()

    def initialize_state(self, loaded_state):
        """Initialize game state from loaded data or new game"""
        if loaded_state:
            return GameState(
                player_deck=loaded_state["player_deck"],
                enemy_deck=loaded_state["enemy_deck"],
                player_score=loaded_state["player_score"],
                enemy_score=loaded_state["enemy_score"],
                total_rounds=loaded_state["total_rounds"],
                player_wins=loaded_state["player_wins"],
                enemy_wins=loaded_state["enemy_wins"],
                ties=loaded_state["ties"],
                cards_played=loaded_state["cards_played"],
                win_streak=loaded_state["win_streak"],
                longest_win_streak=loaded_state["longest_win_streak"],
                played_cards=loaded_state["played_cards"],
                current_war=loaded_state["current_war"],
                current_skirmish=loaded_state["current_skirmish"],
                current_hand=loaded_state["current_hand"],
                player_advantage=loaded_state["player_advantage"],
                enemy_advantage=loaded_state["enemy_advantage"]
            )
        else:
            deck = create_deck()
            shuffle_deck(deck)
            player_deck, enemy_deck = split_deck(deck)
            return GameState(player_deck, enemy_deck)

    def play_hand(self):
        """Play one hand of the game"""
        if not self.state.player_deck or not self.state.enemy_deck:
            return
            
        player_card = self.state.player_deck.pop(0)
        enemy_card = self.state.enemy_deck.pop(0)
        
        result = GameLogic.play_hand(player_card, enemy_card, self.state)
        
        # Update display
        self.create_card_sprites()
        
        # Check game over
        if not self.state.player_deck and not self.state.enemy_deck:
            self.show_game_over()

    def show_game_over(self):
        """Display game over screen"""
        if self.state.player_score > self.state.enemy_score:
            message = "You won the game! You have the most points."
            color = arcade.color.GREEN
        elif self.state.player_score < self.state.enemy_score:
            message = "You lost the game! The enemy has the most points."
            color = arcade.color.RED
        else:
            message = "It's a tie! Both players have the same points."
            color = arcade.color.BLACK
            
        game_over_view = GameOverView(message, color, self)
        self.window.show_view(game_over_view)