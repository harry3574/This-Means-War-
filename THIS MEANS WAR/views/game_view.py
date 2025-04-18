import random
import arcade
from arcade import View, Sprite, SpriteList, gui
from typing import Optional, Dict, Any, List
from game.game_state import WarGameState
from game.deck import Deck, Card
from game.war_logic import WarLogic
from utils.database import db
from constants import *
from utils.tts import TTSHandler
import sqlite3

UNICODE_FONT = "Unifont-JP"

class ProfileSelectionView(View):
    def __init__(self):
        super().__init__()
        self.manager = gui.UIManager()
        self.manager.enable()
        self.profiles: List[dict] = []
        self.selected_profile: Optional[dict] = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        self.manager.clear()
        
        # Main vertical box layout
        self.v_box = gui.UIBoxLayout()
        
        # Title label
        title = gui.UILabel(
            text="Select Profile", 
            font_size=24,
            font_name="Arial"
        )
        self.v_box.add(title)
        self.v_box.add(gui.UISpace(height=20))
        
        # Profile buttons
        self.profiles = db.list_profiles()
        for profile in self.profiles:
            btn = gui.UIFlatButton(
                text=f"{profile.get('emoji', '👤')} {profile['name']}",
                width=300,
                height=40
            )
            btn.on_click = self._make_profile_handler(profile)
            self.v_box.add(btn)
            self.v_box.add(gui.UISpace(height=10))
            
        # New Profile button
        new_btn = gui.UIFlatButton(
            text="➕ New Profile",
            width=300,
            height=40
        )
        new_btn.on_click = self._on_new_profile
        self.v_box.add(new_btn)
        self.v_box.add(gui.UISpace(height=20))
        
        # Quit button
        quit_btn = gui.UIFlatButton(
            text="Exit",
            width=200,
            height=40
        )
        quit_btn.on_click = self._on_exit
        self.v_box.add(quit_btn)
        
        # Anchor layout
        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

    def _make_profile_handler(self, profile: dict):
        def handler(event):
            self.selected_profile = profile
            self._show_saves()
        return handler

    def _show_saves(self):
        """Show save selection view"""
        if self.selected_profile:
            save_view = SaveSelectionView(self.selected_profile)
            self.window.show_view(save_view)

    def _on_new_profile(self, event):
        """Handle new profile button click"""
        # Clear existing UI
        self.manager.clear()
        
        # Create input dialog
        input_box = gui.UIInputText(
            width=300,
            height=40,
            text_color=arcade.color.BLACK,
            font_name="Arial"
        )
        
        # Horizontal layout for input and button
        h_box = gui.UIBoxLayout(vertical=False)
        h_box.add(input_box)
        h_box.add(gui.UISpace(width=10))
        
        submit_btn = gui.UIFlatButton(
            text="Create",
            width=100,
            height=40
        )
        submit_btn.on_click = lambda e: self._create_profile(input_box.text)
        h_box.add(submit_btn)
        
        # Cancel button
        cancel_btn = gui.UIFlatButton(
            text="Cancel",
            width=100,
            height=40
        )
        cancel_btn.on_click = lambda e: self.setup_ui()
        h_box.add(gui.UISpace(width=10))
        h_box.add(cancel_btn)
        
        # Anchor layout for dialog
        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=h_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

    def _create_profile(self, name: str):
        """Create a new profile"""
        if name.strip():
            try:
                profile = db.create_profile(name)
                self.setup_ui()  # Refresh the UI
            except sqlite3.IntegrityError:
                # Show error message
                error = gui.UIMessageBox(
                    width=300,
                    height=160,
                    message_text="Name already exists!",
                    buttons=["OK"]
                )
                anchor = gui.UIAnchorLayout()
                anchor.add(
                    child=error,
                    anchor_x="center",
                    anchor_y="center"
                )
                self.manager.add(anchor)

    def _on_exit(self, event):
        """Handle exit button click"""
        arcade.exit()

    def on_draw(self):
        self.clear()
        self.manager.draw()


class SaveSelectionView(View):
    def __init__(self, profile: dict):
        super().__init__()
        self.profile = profile
        self.manager = gui.UIManager()
        self.manager.enable()
        self.setup_ui()

    def setup_ui(self):
        """Setup the save selection UI"""
        self.manager.clear()
        
        self.v_box = gui.UIBoxLayout()
        
        # Profile header
        header = gui.UILabel(
            text=f"{self.profile.get('emoji', '👤')} {self.profile['name']}",
            font_size=24,
            font_name="Arial"
        )
        self.v_box.add(header)
        self.v_box.add(gui.UISpace(height=20))
        
        # Save slots
        self.saves = db.list_saves(self.profile['id'])
        if self.saves:
            for save in self.saves:
                btn_text = f"War {save['total_rounds']//78 + 1} | Score: {save['player_score']}-{save['enemy_score']}"
                btn = gui.UIFlatButton(
                    text=btn_text,
                    width=400,
                    height=40
                )
                btn.on_click = self._make_save_handler(save['id'])
                self.v_box.add(btn)
                self.v_box.add(gui.UISpace(height=10))
        else:
            no_saves = gui.UILabel(text="No saved games found")
            self.v_box.add(no_saves)
            self.v_box.add(gui.UISpace(height=20))
        
        # Action buttons
        new_btn = gui.UIFlatButton(
            text="🎮 New Game",
            width=400,
            height=40
        )
        new_btn.on_click = self.on_new_game
        self.v_box.add(new_btn)
        self.v_box.add(gui.UISpace(height=10))
        
        back_btn = gui.UIFlatButton(
            text="🔙 Back",
            width=200,
            height=40
        )
        back_btn.on_click = self.on_back
        self.v_box.add(back_btn)
        
        # Anchor layout
        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

    def _make_save_handler(self, save_id: int):
        def handler(event):
            self.load_game(save_id)
        return handler

    def load_game(self, save_id: int):
        """Load a saved game"""
        saved_state = db.load_game_state(self.profile['id'], save_id)
        if saved_state:
            game_view = GameView()
            game_view.setup(saved_state)
            self.window.show_view(game_view)

    def on_new_game(self, event):
        """Start a new game"""
        game_view = GameView()
        game_view.current_profile_id = self.profile['id']
        game_view.setup()
        self.window.show_view(game_view)

    def on_back(self, event):
        """Return to profile selection"""
        self.window.show_view(ProfileSelectionView())

    def on_draw(self):
        self.clear()
        self.manager.draw()

# game/views/game_view.py
import arcade
from arcade import View, Sprite, SpriteList, gui
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from constants import *
from game.deck import Deck, Card
from game.game_state import WarGameState
from game.war_logic import WarLogic
from views.stats_view import StatsView
from utils.tts import TTSHandler

@dataclass
class CardSprite:
    """Wrapper for card display logic"""
    card: Card
    sprite: Sprite
    face_up: bool = False

class GameView(View):
    def __init__(self, profile_id: Optional[int] = None, loaded_state: Optional[Dict] = None):
        super().__init__()
        self.profile_id = profile_id
        self.game_state = WarGameState()
        self.war_logic = WarLogic()
        self.tts = TTSHandler()
        
        # Visual elements
        self.card_sprites: List[CardSprite] = []
        self.ui_manager = gui.UIManager()
        self.setup_ui()
        
        # Game setup
        if loaded_state:
            self.load_state(loaded_state)
        else:
            self.initialize_new_game()
        
        # State tracking
        self.current_outcome: Optional[str] = None
        self.outcome_timer: float = 0
        self.animation_state: Dict[str, Any] = {}

    def setup_ui(self):
        """Initialize the UI elements"""
        self.ui_manager.enable()
        
        # Create button panel
        button_panel = gui.UIBoxLayout(vertical=False)
        
        # Peek button
        peek_btn = gui.UIFlatButton(text="Peek", width=100)
        peek_btn.on_click = self.on_peek_click
        button_panel.add(peek_btn.with_padding(right=10))
        
        # Stats button
        stats_btn = gui.UIFlatButton(text="Stats", width=100)
        stats_btn.on_click = self.on_stats_click
        button_panel.add(stats_btn.with_padding(right=10))
        
        # Draw button
        draw_btn = gui.UIFlatButton(text="Draw", width=100)
        draw_btn.on_click = self.on_draw_click
        button_panel.add(draw_btn.with_padding(right=10))
        
        # Save button
        save_btn = gui.UIFlatButton(text="Save", width=100)
        save_btn.on_click = self.on_save_click
        button_panel.add(save_btn)
        
        # Add panel to view
        self.ui_manager.add(
            gui.UIAnchorLayout(
                anchor_x="center",
                anchor_y="bottom",
                child=button_panel,
                align_y=50
            )
        )

    def initialize_new_game(self):
        """Start a fresh game session"""
        deck = Deck()
        deck.shuffle()
        self.game_state.player_deck, self.game_state.enemy_deck = deck.split()
        self.create_card_sprites()

    def load_state(self, state: Dict):
        """Load game from saved state"""
        for key, value in state.items():
            setattr(self.game_state, key, value)
        self.create_card_sprites()

    def create_card_sprites(self):
        """Create visual representations of cards"""
        self.card_sprites.clear()
        
        # Player card (face up)
        if self.game_state.player_deck:
            player_card = self.game_state.player_deck[0]
            sprite = self._create_card_sprite(player_card, 400, 200, face_up=True)
            self.card_sprites.append(CardSprite(player_card, sprite, True))
        
        # Enemy card (face down unless in animation)
        if self.game_state.enemy_deck:
            enemy_card = self.game_state.enemy_deck[0]
            sprite = self._create_card_sprite(enemy_card, 800, 200, face_up=False)
            self.card_sprites.append(CardSprite(enemy_card, sprite, False))

    def _create_card_sprite(self, card: Card, x: float, y: float, face_up: bool) -> Sprite:
        """Helper to create a card sprite"""
        # In a real implementation, you'd use actual card images
        sprite = arcade.SpriteSolidColor(
            width=120, 
            height=180,
            color=arcade.color.WHITE if face_up else arcade.color.BLUE
        )
        sprite.position = x, y
        return sprite

    def on_draw(self):
        arcade.start_render()
        
        # Draw game info
        self.draw_game_info()
        
        # Draw cards
        for card_sprite in self.card_sprites:
            card_sprite.sprite.draw_hit_box()
            
            # Draw card details if face up
            if card_sprite.face_up:
                arcade.draw_text(
                    card_sprite.card.rank,
                    card_sprite.sprite.center_x - 30,
                    card_sprite.sprite.center_y,
                    arcade.color.RED if card_sprite.card.suit in ['♥', '♦'] else arcade.color.BLACK,
                    24,
                    anchor_x="center"
                )
                arcade.draw_text(
                    card_sprite.card.suit,
                    card_sprite.sprite.center_x + 30,
                    card_sprite.sprite.center_y,
                    arcade.color.RED if card_sprite.card.suit in ['♥', '♦'] else arcade.color.BLACK,
                    24,
                    anchor_x="center"
                )
        
        # Draw outcome message if any
        if self.current_outcome:
            arcade.draw_text(
                self.current_outcome,
                self.window.width // 2,
                self.window.height // 2 + 100,
                arcade.color.BLACK,
                36,
                anchor_x="center"
            )
        
        # Draw UI
        self.ui_manager.draw()

    def draw_game_info(self):
        """Render all game status information"""
        # Scores
        arcade.draw_text(
            f"Player: {self.game_state.player_score}",
            100, self.window.height - 50,
            arcade.color.GREEN, 24
        )
        arcade.draw_text(
            f"Enemy: {self.game_state.enemy_score}",
            self.window.width - 150, self.window.height - 50,
            arcade.color.RED, 24
        )
        
        # War progress
        arcade.draw_text(
            f"War {self.game_state.current_war} - "
            f"Skirmish {self.game_state.current_skirmish} - "
            f"Hand {self.game_state.current_hand}",
            self.window.width // 2,
            self.window.height - 50,
            arcade.color.BLACK, 24,
            anchor_x="center"
        )
        
        # Advantage
        arcade.draw_text(
            f"Advantage: {self.game_state.player_advantage}/{self.game_state.score_to_beat}",
            self.window.width // 2,
            self.window.height - 80,
            arcade.color.GREEN if self.game_state.player_advantage >= self.game_state.score_to_beat 
            else arcade.color.RED,
            20,
            anchor_x="center"
        )

    def on_update(self, delta_time: float):
        """Handle animations and timed events"""
        if self.current_outcome:
            self.outcome_timer -= delta_time
            if self.outcome_timer <= 0:
                self.current_outcome = None
                
        # Update any active animations
        self.update_animations(delta_time)

    def update_animations(self, delta_time: float):
        """Process any running animations"""
        # This would handle card flip/draw animations in a full implementation
        pass

    def on_draw_click(self, event):
        """Handle draw button click"""
        if self.current_outcome:
            return  # Don't allow draws during outcome display
            
        result = self.war_logic.resolve_hand(self.game_state)
        self.handle_resolution(result)

    def handle_resolution(self, result: str):
        """Process the outcome of a hand resolution"""
        outcomes = {
            "continue": None,
            "player_win": "You won this hand!",
            "enemy_win": "Enemy won this hand!",
            "skirmish_complete": "Skirmish complete!",
            "war_complete": "War complete!",
            "game_over": "Game Over!"
        }
        
        if result in outcomes:
            self.current_outcome = outcomes[result]
            self.outcome_timer = 2.0  # Show message for 2 seconds
            
        # Update card display
        self.create_card_sprites()
        
        # Special handling for game over
        if result == "game_over":
            self.handle_game_over()

    def handle_game_over(self):
        """Transition to game over state"""
        # In a full implementation, this would show a game over screen
        #from views.menu_view import 
        #self.window.show_view(Menu())

    def on_peek_click(self, event):
        """Switch to peek view"""
        peek_view = PeekView(self.game_state)
        peek_view.previous_view = self
        self.window.show_view(peek_view)

    def on_stats_click(self, event):
        """Switch to stats view"""
        stats_view = StatsView(self.game_state)
        stats_view.previous_view = self
        self.window.show_view(stats_view)

    def on_save_click(self, event):
        """Save current game state"""
        if self.profile_id:
            from database import db
            db.save_game_state(self.profile_id, self.game_state.__dict__)
            self.current_outcome = "Game Saved!"
            self.outcome_timer = 1.5

    def on_key_press(self, key, modifiers):
        """Handle keyboard shortcuts"""
        if key == arcade.key.SPACE:
            self.on_draw_click(None)
        elif key == arcade.key.P:
            self.on_peek_click(None)
        elif key == arcade.key.S:
            self.on_stats_click(None)
        elif key == arcade.key.F5:
            self.on_save_click(None)
        elif key == arcade.key.F3:
            self.announce_state()

    def announce_state(self):
        """Use TTS to announce game state"""
        message = (
            f"War {self.game_state.current_war}, "
            f"Skirmish {self.game_state.current_skirmish}, "
            f"Hand {self.game_state.current_hand}. "
            f"Player score: {self.game_state.player_score}, "
            f"Enemy score: {self.game_state.enemy_score}. "
            f"Advantage: {self.game_state.player_advantage} "
            f"out of {self.game_state.score_to_beat} needed."
        )
        self.tts.speak(message)