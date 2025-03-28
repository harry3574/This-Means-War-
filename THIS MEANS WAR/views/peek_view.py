import arcade
from arcade import View, SpriteList, Sprite, gui
from typing import Optional
from game.deck import Card
from game.game_state import WarGameState
from constants import *

class PeekView(View):
    def __init__(self, game_state: WarGameState):
        super().__init__()
        self.game_state = game_state
        self.cursor_pos = 0
        self.selected_pos: Optional[int] = None
        self.scroll_offset = 0
        self.visible_cards = 5
        self.card_sprites = SpriteList()
        
        # UI Manager
        self.manager = gui.UIManager()
        self.manager.enable()
        
        # Back button
        back_button = gui.UIFlatButton(text="Exit Peek", width=200)
        back_button.on_click = self.on_back_click
        self.manager.add(
            gui.UIAnchorWidget(
                anchor_x="center",
                anchor_y="bottom",
                child=back_button,
                align_y=20
            )
        )
        
        self.setup_card_sprites()
    
    def setup_card_sprites(self):
        """Create sprite representations of cards"""
        self.card_sprites.clear()
        card_width, card_height = 100, 150
        spacing = 20
        
        # Player cards
        for i in range(self.scroll_offset, min(len(self.game_state.player_deck), self.scroll_offset + self.visible_cards)):
            card = self.game_state.player_deck[i]
            x = 50 + (i - self.scroll_offset) * (card_width + spacing)
            y = 300
            
            # Create card background
            bg_color = (
                PASTEL_CYAN if i == self.selected_pos else
                PASTEL_YELLOW if i == self.cursor_pos else
                WHITE
            )
            
            card_sprite = arcade.SpriteSolidColor(card_width, card_height, bg_color)
            card_sprite.position = x + card_width/2, y + card_height/2
            self.card_sprites.append(card_sprite)
            
            # Add card text
            self.card_sprites.append(self._create_text_sprite(
                card.rank, x + 10, y + 10, 
                RED if card.suit in ['♥', '♦'] else BLACK
            ))
            
        # Enemy cards (simplified)
        for i in range(self.scroll_offset, min(len(self.game_state.enemy_deck), self.scroll_offset + self.visible_cards)):
            card = self.game_state.enemy_deck[i]
            x = 50 + (i - self.scroll_offset) * (card_width + spacing)
            y = 150
            
            card_sprite = arcade.SpriteSolidColor(card_width, card_height, WHITE)
            card_sprite.position = x + card_width/2, y + card_height/2
            self.card_sprites.append(card_sprite)
            
            # Only show enemy card backs unless hovered
            if i == self.cursor_pos:
                self.card_sprites.append(self._create_text_sprite(
                    card.rank, x + 10, y + 10, 
                    RED if card.suit in ['♥', '♦'] else BLACK
                ))
            else:
                # Draw card back pattern
                pass
    
    def _create_text_sprite(self, text: str, x: float, y: float, color) -> Sprite:
        """Helper to create text as sprites for batch drawing"""
        label = arcade.Text(
            text=text,
            start_x=x,
            start_y=y,
            color=color,
            font_size=18
        )
        # Note: Arcade doesn't easily support Text in SpriteLists
        # This is a simplified approach - for production, consider:
        # 1. Using custom shaders
        # 2. Drawing text separately
        # 3. Using texture-based text rendering
        return label  # This won't actually work as a sprite - needs refinement
    
    def on_draw(self):
        arcade.start_render()
        self.card_sprites.draw()
        self.manager.draw()
        
        # Draw labels
        arcade.draw_text("Enemy Deck:", 50, 400, BLACK, 24)
        arcade.draw_text("Your Deck:", 50, 200, BLACK, 24)
        
        # Draw instructions
        arcade.draw_text(
            "Use ARROWS to navigate, ENTER to select, ESC to exit",
            50, 50, BLACK, 16
        )
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif key == arcade.key.DOWN:
            self.cursor_pos = min(len(self.game_state.player_deck) - 1, self.cursor_pos + 1)
        elif key == arcade.key.LEFT:
            if self.cursor_pos > 0:
                self.cursor_pos -= 1
                if self.cursor_pos < self.scroll_offset:
                    self.scroll_offset = max(0, self.cursor_pos)
        elif key == arcade.key.RIGHT:
            if self.cursor_pos < len(self.game_state.player_deck) - 1:
                self.cursor_pos += 1
                if self.cursor_pos >= self.scroll_offset + self.visible_cards:
                    self.scroll_offset = min(
                        len(self.game_state.player_deck) - self.visible_cards,
                        self.cursor_pos - self.visible_cards + 1
                    )
        elif key == arcade.key.ENTER:
            if self.selected_pos is None:
                self.selected_pos = self.cursor_pos
            else:
                # Swap cards
                self.game_state.player_deck[self.selected_pos], self.game_state.player_deck[self.cursor_pos] = (
                    self.game_state.player_deck[self.cursor_pos], self.game_state.player_deck[self.selected_pos]
                )
                self.selected_pos = None
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.previous_view)
        
        self.setup_card_sprites()
    
    def on_back_click(self, event):
        self.window.show_view(self.previous_view)