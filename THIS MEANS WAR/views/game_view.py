# game/game_view.py
import arcade
from arcade import View, SpriteList
from typing import Optional, Dict, Any
from pathlib import Path

# Import other views
from views.peek_view import PeekView
from views.stats_view import StatsView
from views.menu_view import MenuView
from views.game_over_view import GameOverView

# Import game components
from game.card import CardSprite
from game.deck import create_deck, shuffle_deck, split_deck
from game.state import GameState
from game.tts import TTSHandler

# Import utilities
from utils.database import save_game

class GameView(View):
    def __init__(self, profile_id: int, loaded_state: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.profile_id = profile_id
        self.state = self._initialize_state(loaded_state)
        self.card_sprites = SpriteList()
        self.ui_elements = SpriteList()
        self.tts = TTSHandler()
        self.setup()

    def _initialize_state(self, loaded_state: Optional[Dict[str, Any]]) -> GameState:
        """Initialize game state from loaded data or new game"""
        if loaded_state:
            return GameState(
                player_deck=loaded_state["player_deck"],
                enemy_deck=loaded_state["enemy_deck"],
                # ... (all other loaded state fields)
            )
        else:
            deck = create_deck()
            shuffle_deck(deck)
            player_deck, enemy_deck = split_deck(deck)
            return GameState(player_deck, enemy_deck)

    def setup(self):
        """Set up the game view"""
        self._create_card_sprites()
        self._create_ui_elements()

    def _create_card_sprites(self):
        """Create sprites for the current cards"""
        self.card_sprites.clear()
        
        if self.state.player_deck:
            player_card = CardSprite(
                self.state.player_deck[0],
                center_x=self.window.width // 3,
                center_y=self.window.height // 2,
                is_player=True
            )
            self.card_sprites.append(player_card)
        
        if self.state.enemy_deck:
            enemy_card = CardSprite(
                self.state.enemy_deck[0],
                center_x=self.window.width * 2 // 3,
                center_y=self.window.height // 2,
                is_player=False
            )
            self.card_sprites.append(enemy_card)

    def _create_ui_elements(self):
        """Create UI text elements"""
        self.ui_elements.clear()
        
        # Score displays
        player_score = arcade.Text(
            f"Player: {self.state.player_score}",
            self.window.width // 3,
            self.window.height - 50,
            arcade.color.BLACK,
            24,
            anchor_x="center"
        )
        self.ui_elements.append(player_score)
        
        enemy_score = arcade.Text(
            f"Enemy: {self.state.enemy_score}",
            self.window.width * 2 // 3,
            self.window.height - 50,
            arcade.color.BLACK,
            24,
            anchor_x="center"
        )
        self.ui_elements.append(enemy_score)

    def on_draw(self):
        """Render the game"""
        arcade.start_render()
        self.card_sprites.draw()
        
        # Draw war/skirmish info
        arcade.draw_text(
            f"War {self.state.current_war} - Skirmish {self.state.current_skirmish} - Hand {self.state.current_hand}",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.BLACK,
            24,
            anchor_x="center"
        )
        
        # Draw advantage info
        advantage_text = f"Player Advantage: {self.state.player_advantage}/{self.state.score_to_beat}"
        arcade.draw_text(
            advantage_text,
            self.window.width // 2,
            self.window.height - 130,
            arcade.color.GREEN if self.state.player_advantage >= self.state.score_to_beat else arcade.color.RED,
            24,
            anchor_x="center"
        )
        
        # Draw instructions
        instructions = [
            "SPACE: Play Hand",
            "P: Peek at Decks", 
            "S: View Stats",
            "F5: Save Game",
            "ESC: Return to Menu"
        ]
        for i, text in enumerate(instructions):
            arcade.draw_text(
                text,
                20,
                30 + i * 30,
                arcade.color.BLACK,
                18
            )

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.SPACE:
            self._play_hand()
        elif key == arcade.key.P:
            self.window.show_view(PeekView(self))
        elif key == arcade.key.S:
            self.window.show_view(StatsView(self.state))
        elif key == arcade.key.F5:
            save_game(self.profile_id, self.state)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView(self.profile_id))

    def _play_hand(self):
        """Process playing a single hand"""
        if not self.state.player_deck or not self.state.enemy_deck:
            return
            
        player_card = self.state.player_deck.pop(0)
        enemy_card = self.state.enemy_deck.pop(0)
        
        # Update game state (would call to game logic)
        self.state.played_cards.extend([player_card['rank'], enemy_card['rank']])
        self.state.cards_played += 2
        
        # Check for game over
        if not self.state.player_deck and not self.state.enemy_deck:
            self._handle_game_over()
        else:
            self._create_card_sprites()

    def _handle_game_over(self):
        """Show game over screen"""
        if self.state.player_score > self.state.enemy_score:
            message = "You won the game!"
            color = arcade.color.GREEN
        elif self.state.enemy_score > self.state.player_score:
            message = "You lost the game!"
            color = arcade.color.RED
        else:
            message = "It's a tie!"
            color = arcade.color.BLACK
            
        self.window.show_view(GameOverView(message, color, self.profile_id))