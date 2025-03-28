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


import arcade
from arcade import View, SpriteList, Sprite
from typing import Optional, Dict
from game.deck import Card
from game.game_state import WarGameState
from game.war_logic import WarLogic
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, UNICODE_FONT

class GameView(View):
    def __init__(self):
        super().__init__()
        self.game_state = WarGameState()
        self.card_sprites = SpriteList()
        self.war_logic = WarLogic()
        self.tts = TTSHandler()
        
        # Card positions for 1280x720 screen
        self.player_card_pos = (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 100)
        self.enemy_card_pos = (SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2 - 100)
        
        # Initialize UI
        self.manager = gui.UIManager()
        self.manager.enable()
        self.setup_ui()

    def setup(self, loaded_state: Optional[Dict] = None):
        """Initialize game state with proper card values"""
        if loaded_state:
            self.game_state.__dict__.update(loaded_state)
        else:
            # Initialize new game with proper card values
            rank_values = {
                '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
            }
            deck = [
                Card(rank=rank, suit=suit, value=rank_values[rank])
                for suit in ['♥', '♦', '♣', '♠']
                for rank in rank_values.keys()
            ]
            self.war_logic.shuffle_deck(deck)
            self.game_state.player_deck = deck[:26]
            self.game_state.enemy_deck = deck[26:]
        
        self._create_card_sprites()

    def _create_card_sprites(self):
        """Create card sprites with proper positioning"""
        self.card_sprites.clear()
        
        # Player card
        if self.game_state.player_deck:
            player_sprite = arcade.SpriteSolidColor(100, 150, arcade.color.WHITE)
            player_sprite.position = self.player_card_pos
            self.card_sprites.append(player_sprite)
            self._add_card_text(self.game_state.player_deck[0], *self.player_card_pos)
        
        # Enemy card
        if self.game_state.enemy_deck:
            enemy_sprite = arcade.SpriteSolidColor(100, 150, arcade.color.WHITE)
            enemy_sprite.position = self.enemy_card_pos
            self.card_sprites.append(enemy_sprite)
            self._add_card_text(self.game_state.enemy_deck[0], *self.enemy_card_pos)

    def _add_card_text(self, card: Card, x: float, y: float):
        """Draw card text elements at specified positions with proper coordinates"""
        # Card background coordinates (center of card)
        card_center_x = x
        card_center_y = y
        
        # Rank position (top left quadrant)
        rank_x = card_center_x - 30  # 30 pixels left of center
        rank_y = card_center_y + 30  # 30 pixels above center
        
        # Suit position (bottom right quadrant)
        suit_x = card_center_x + 30  # 30 pixels right of center
        suit_y = card_center_y - 30  # 30 pixels below center
        
        # Determine card color based on suit
        card_color = arcade.color.RED if card.suit in ['♥', '♦'] else arcade.color.BLACK
        
        # Draw rank text
        arcade.Text(
            text=card.rank,
            start_x=rank_x,
            start_y=rank_y,
            color=card_color,
            font_size=24,
            font_name=UNICODE_FONT,
            anchor_x="center",
            anchor_y="center"
        ).draw()
        
        # Draw suit text
        arcade.Text(
            text=card.suit,
            start_x=suit_x,
            start_y=suit_y,
            color=card_color,
            font_size=24,
            font_name=UNICODE_FONT,
            anchor_x="center",
            anchor_y="center"
        ).draw()

    def on_draw(self):
        arcade.start_render()
        
        # Draw scores
        arcade.draw_text(
            f"Player: {self.game_state.player_score}",
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT - 50,
            arcade.color.BLUE,
            24,
            anchor_x="center",
            font_name=UNICODE_FONT
        )
        
        arcade.draw_text(
            f"Enemy: {self.game_state.enemy_score}",
            SCREEN_WIDTH * 3 // 4,
            SCREEN_HEIGHT - 50,
            arcade.color.RED,
            24,
            anchor_x="center",
            font_name=UNICODE_FONT
        )
        
        # Draw war info
        arcade.draw_text(
            f"War {self.game_state.current_war} - "
            f"Skirmish {self.game_state.current_skirmish} - "
            f"Hand {self.game_state.current_hand}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.BLACK,
            20,
            anchor_x="center",
            font_name=UNICODE_FONT
        )
        
        # Draw cards
        self.card_sprites.draw()
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.play_hand()
        elif key == arcade.key.P:
            self.on_peek(None)
        elif key == arcade.key.ESCAPE:
            self.show_pause_menu(None)
        elif key == arcade.key.F3:
            self.announce_state()

    def play_hand(self):
        """Play a single hand of war"""
        try:
            result = self.war_logic.resolve_hand(self.game_state)
            
            if result == "game_over":
                self.handle_game_over()
            else:
                self._create_card_sprites()
            
            # Auto-save if needed
            if hasattr(self, 'current_profile_id'):
                self._save_game_state()
                
        except Exception as e:
            print(f"Error playing hand: {e}")

    def _save_game_state(self):
        """Save current game state"""
        if hasattr(self, 'current_profile_id'):
            db.save_game_state(
                self.current_profile_id,
                {
                    'player_deck': [c.__dict__ for c in self.game_state.player_deck],
                    'enemy_deck': [c.__dict__ for c in self.game_state.enemy_deck],
                    'player_score': self.game_state.player_score,
                    'enemy_score': self.game_state.enemy_score,
                    'current_war': self.game_state.current_war,
                    'current_skirmish': self.game_state.current_skirmish,
                    'current_hand': self.game_state.current_hand,
                    'player_advantage': self.game_state.player_advantage,
                    'enemy_advantage': self.game_state.enemy_advantage
                }
            )

    def handle_game_over(self):
        """Handle game end condition"""
        from views.menu_view import EndGameView
        
        if self.game_state.player_score > self.game_state.enemy_score:
            winner = "Player"
        elif self.game_state.player_score < self.game_state.enemy_score:
            winner = "Enemy"
        else:
            winner = "Tie"
        
        end_view = EndGameView(winner, self.game_state)
        self.window.show_view(end_view)

    def on_draw(self):
        arcade.start_render()
        
        # Draw all sprites
        self.card_sprites.draw()
        
        # Draw all text objects
        for text in self.card_texts:
            text.draw()
        
        # Draw other UI elements
        self.manager.draw()
    

    def _add_card_text(self, card: Card, x: float, y: float):
        """Helper to create card text elements with proper positioning"""
        # Card rank text (top left)
        rank_text = arcade.Text(
            text=card.rank,
            start_x=x - 30,
            start_y=y + 30,  # Adjusted for better positioning
            color=arcade.color.RED if card.suit in ['♥', '♦'] else arcade.color.BLACK,
            font_size=24,
            font_name=UNICODE_FONT,
            anchor_x="center",
            anchor_y="center"
        )
        rank_text.draw()

        # Card suit text (bottom right)
        suit_text = arcade.Text(
            text=card.suit,
            start_x=x + 30,
            start_y=y - 30,  # Adjusted for better positioning
            color=arcade.color.RED if card.suit in ['♥', '♦'] else arcade.color.BLACK,
            font_size=24,
            font_name=UNICODE_FONT,
            anchor_x="center",
            anchor_y="center"
        )
        suit_text.draw()
    
    
    def setup_ui(self):
        """Create in-game UI elements without UIAnchorWidget"""
        self.manager.clear()
        
        # Create a main layout that fills the screen
        main_layout = gui.UIBoxLayout(vertical=False)
        
        # Left spacer
        left_spacer = gui.UISpace(width=20)
        main_layout.add(left_spacer)
        
        # Center content area
        center_layout = gui.UIBoxLayout(vertical=True)
        
        # Top spacer for pause button
        top_spacer = gui.UISpace(height=20)
        center_layout.add(top_spacer)
        
        # Pause button row
        pause_row = gui.UIBoxLayout(vertical=False)
        pause_row.add(gui.UISpace(width=self.window.width - 100))  # Push button to right
        pause_btn = gui.UIFlatButton(text="≡", width=40, height=40)
        pause_btn.on_click = self.show_pause_menu
        pause_row.add(pause_btn)
        center_layout.add(pause_row)
        
        # Middle spacer
        center_layout.add(gui.UISpace(height=self.window.height - 200))
        
        # Peek button row
        peek_btn = gui.UIFlatButton(text="👁️ Peek", width=100)
        peek_btn.on_click = self.on_peek
        center_layout.add(peek_btn)
        
        # Add center layout to main layout
        main_layout.add(center_layout)
        
        # Right spacer
        right_spacer = gui.UISpace(width=20)
        main_layout.add(right_spacer)
        
        self.manager.add(main_layout)

    def on_draw(self):
        self.clear()
        
        # Draw scores
        arcade.draw_text(
            f"Player: {self.game_state.player_score}",
            self.window.width // 4,
            self.window.height - 50,
            arcade.color.BLUE,
            24,
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"Enemy: {self.game_state.enemy_score}",
            self.window.width * 3 // 4,
            self.window.height - 50,
            arcade.color.RED,
            24,
            anchor_x="center"
        )
        
        # Draw war info
        arcade.draw_text(
            f"War {self.game_state.current_war} "
            f"- Skirmish {self.game_state.current_skirmish} "
            f"- Hand {self.game_state.current_hand}",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.BLACK,
            20,
            anchor_x="center"
        )
        
        # Draw advantage
        arcade.draw_text(
            f"Advantage: {self.game_state.player_advantage}/{self.game_state.score_to_beat}",
            self.window.width // 2,
            100,
            GREEN if self.game_state.player_advantage >= self.game_state.score_to_beat else RED,
            24,
            anchor_x="center"
        )
        
        # Draw cards
        self.card_sprites.draw()
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.play_hand()
        elif key == arcade.key.P:
            self.on_peek(None)
        elif key == arcade.key.ESCAPE:
            self.show_pause_menu(None)
        elif key == arcade.key.F3:  # TTS
            self.announce_state()

    def play_hand(self):
        """Play a single hand of war"""
        # Initialize WarLogic with the current seed if you have one
        war_logic = WarLogic(seed=self.game_state.current_seed)  # Assuming you store the seed
        
        try:
            result = war_logic.resolve_hand(self.game_state)
            
            if result == "game_over":
                self.handle_game_over()
            elif result in ["skirmish_complete", "war_complete"]:
                # Update UI to reflect new skirmish/war state
                self._update_game_display()
                
                # Optional: Show a message about the completed skirmish/war
                if result == "war_complete":
                    self.show_message(f"War {self.game_state.current_war-1} completed!")
                else:
                    self.show_message("Skirmish completed!")
            
            # Update visuals
            self._create_card_sprites()
            self._update_text_objects()
            
            # Auto-save if needed
            if hasattr(self, 'current_profile_id'):
                self._save_game_state()
                
        except Exception as e:
            print(f"Error resolving hand: {e}")
            # Fallback or error handling

    def handle_game_over(self):
        """Transition to game over view"""
        from views.menu_view import EndGameView
        
        if self.game_state.player_score > self.game_state.enemy_score:
            winner = "Player"
        elif self.game_state.player_score < self.game_state.enemy_score:
            winner = "Enemy"
        else:
            winner = "Tie"
        
        end_view = EndGameView(winner, self.game_state)
        self.window.show_view(end_view)

    def announce_state(self):
        """TTS announcement of current game state"""
        msg = (
            f"War {self.game_state.current_war}, "
            f"Skirmish {self.game_state.current_skirmish}, "
            f"Hand {self.game_state.current_hand}. "
            f"Score: Player {self.game_state.player_score}, "
            f"Enemy {self.game_state.enemy_score}. "
            f"Advantage: {self.game_state.player_advantage} "
            f"out of {self.game_state.score_to_beat} needed."
        )
        self.tts.speak(msg)

    def on_peek(self, event):
        """Show peek view"""
        from views.peek_view import PeekView
        peek_view = PeekView(self.game_state)
        peek_view.previous_view = self
        self.window.show_view(peek_view)

    def show_pause_menu(self, event):
        """Display pause menu without UIAnchorWidget"""
        self.manager.clear()
        
        # Create overlay background
        overlay_bg = arcade.SpriteSolidColor(
            self.window.width, 
            self.window.height, 
            arcade.color.BLACK
        )
        overlay_bg.color = (0, 0, 0, 200)  # Semi-transparent
        overlay_bg.position = self.window.width // 2, self.window.height // 2
        
        # Create menu layout
        menu_layout = gui.UIBoxLayout(vertical=True)
        
        if self.current_profile_id:
            save_btn = gui.UIFlatButton(text="💾 Save", width=200)
            save_btn.on_click = self.on_save_game
            menu_layout.add(save_btn)
            menu_layout.add(gui.UISpace(height=10))
        
        stats_btn = gui.UIFlatButton(text="📊 Stats", width=200)
        stats_btn.on_click = self.on_show_stats
        menu_layout.add(stats_btn)
        menu_layout.add(gui.UISpace(height=10))
        
        quit_btn = gui.UIFlatButton(text="🚪 Quit", width=200)
        quit_btn.on_click = self.on_quit
        menu_layout.add(quit_btn)
        
        # Create a centered layout using spacers
        outer_layout = gui.UIBoxLayout(vertical=True)
        outer_layout.add(gui.UISpace(height=self.window.height // 3))
        
        mid_layout = gui.UIBoxLayout(vertical=False)
        mid_layout.add(gui.UISpace(width=self.window.width // 3))
        mid_layout.add(menu_layout)
        
        outer_layout.add(mid_layout)
        
        self.manager.add(outer_layout)
        
        # Store background reference for drawing
        self.pause_overlay_bg = overlay_bg
    
    def on_save_game(self, event):
        """Handle save game"""
        if self.current_profile_id:
            save_id = db.save_game_state(
                self.current_profile_id,
                self.game_state.__dict__
            )
            self.manager.clear()
            self.setup_ui()
            msg = f"Game saved as ID {save_id}"
            self.tts.speak(msg)
            
            # Show confirmation
            confirm = gui.UIMessageBox(
                width=300,
                height=150,
                title="Saved",
                message=msg,
                buttons=["OK"]
            )
            self.manager.add(confirm)

    def on_show_stats(self, event):
        """Show statistics view"""
        from views.stats_view import StatsView
        self.manager.clear()
        stats_view = StatsView(self.game_state)
        stats_view.previous_view = self
        self.window.show_view(stats_view)

    def on_quit(self, event):
        """Return to main menu"""
        self.window.show_view(ProfileSelectionView())