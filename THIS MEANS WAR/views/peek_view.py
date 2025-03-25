# views/peek_view.py
import arcade
from arcade import View, SpriteList
from game.card import CardSprite
from constants import WIDTH, HEIGHT, GREEN, RED, BLUE


class PeekView(View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view  # Reference to parent game view
        self.cursor_pos = 0
        self.selected_pos = None
        self.scroll_offset = 0
        self.card_sprites = SpriteList()
        self.ui_text = SpriteList()
        
        # Calculate layout parameters
        self.card_width = 100
        self.card_height = 150
        self.spacing = 20
        self.visible_cards = WIDTH // (self.card_width + self.spacing)
        
        self.setup()

    def setup(self):
        """Initialize the peek view"""
        self.create_card_sprites()
        self.create_ui_elements()

    def create_card_sprites(self):
        """Create card sprites for both decks"""
        # Clear existing sprites
        self.card_sprites.clear()
        
        # Enemy deck (top)
        enemy_y = HEIGHT - 200
        for i in range(self.scroll_offset, 
                      min(len(self.game_view.enemy_deck), 
                      self.scroll_offset + self.visible_cards)):
            card = self.game_view.enemy_deck[i]
            x = 50 + (i - self.scroll_offset) * (self.card_width + self.spacing)
            
            sprite = CardSprite(
                card,
                center_x=x + self.card_width//2,
                center_y=enemy_y - self.card_height//2,
                is_player=False,
                hovered=(i == self.cursor_pos)
            )
            self.card_sprites.append(sprite)

        # Player deck (bottom)
        player_y = HEIGHT // 2
        for i in range(self.scroll_offset, 
                      min(len(self.game_view.player_deck), 
                      self.scroll_offset + self.visible_cards)):
            card = self.game_view.player_deck[i]
            x = 50 + (i - self.scroll_offset) * (self.card_width + self.spacing)
            
            sprite = CardSprite(
                card,
                center_x=x + self.card_width//2,
                center_y=player_y - self.card_height//2,
                is_player=True,
                hovered=(i == self.cursor_pos),
                selected=(i == self.selected_pos)
            )
            self.card_sprites.append(sprite)

    def create_ui_elements(self):
        """Create UI text elements"""
        self.ui_text.clear()
        
        # Enemy deck label
        enemy_label = arcade.Text(
            "Enemy Deck (Next Cards):",
            50, HEIGHT - 150,
            RED, 24
        )
        self.ui_text.append(enemy_label)
        
        # Player deck label
        player_label = arcade.Text(
            "Your Deck (Next Cards):",
            50, HEIGHT // 2 - 100,
            GREEN, 24
        )
        self.ui_text.append(player_label)
        
        # Instructions
        instructions = [
            "Use LEFT/RIGHT to scroll, UP/DOWN to move",
            "ENTER to select/swap, 'P' to exit",
            "Selected card highlighted in CYAN"
        ]
        for i, line in enumerate(instructions):
            text = arcade.Text(
                line,
                10, 30 + i * 30,
                arcade.color.BLACK, 20
            )
            self.ui_text.append(text)

    def on_draw(self):
        """Render the peek view"""
        arcade.start_render()
        
        # Draw cards and UI
        self.card_sprites.draw()
        
        # Draw advantage points between decks
        self.draw_advantage_points()
        
        # Draw UI text
        for text in self.ui_text:
            text.draw()

    def draw_advantage_points(self):
        """Draw advantage points between card pairs"""
        player_y = HEIGHT // 2 - 100
        enemy_y = HEIGHT - 200
        
        for i in range(self.scroll_offset, 
                      min(len(self.game_view.player_deck), 
                      self.scroll_offset + self.visible_cards)):
            if i >= len(self.game_view.enemy_deck):
                break
                
            player_card = self.game_view.player_deck[i]
            enemy_card = self.game_view.enemy_deck[i]
            advantage = self.calculate_advantage(player_card, enemy_card)
            
            x = 50 + (i - self.scroll_offset) * (self.card_width + self.spacing) + self.card_width//2
            y = (player_y + enemy_y) // 2
            
            color = GREEN if advantage >= 0 else RED
            text = f"{'+' if advantage >= 0 else ''}{advantage}"
            
            arcade.draw_text(
                text, x, y,
                color, 24,
                anchor_x="center", anchor_y="center"
            )

    def calculate_advantage(self, player_card, enemy_card):
        """Calculate advantage points (from your original logic)"""
        rank_order = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        suit_order = {'♥': 4, '♦': 3, '♣': 2, '♠': 1}
        
        player_rank = rank_order.index(player_card['rank'])
        enemy_rank = rank_order.index(enemy_card['rank'])
        rank_diff = player_rank - enemy_rank
        
        player_suit = suit_order.get(player_card['suit'], 0)
        enemy_suit = suit_order.get(enemy_card['suit'], 0)
        suit_diff = player_suit - enemy_suit
        
        return (rank_diff * 2) + suit_diff

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.UP:
            self.cursor_pos = max(0, self.cursor_pos - 1)
            if self.cursor_pos < self.scroll_offset:
                self.scroll_offset = max(0, self.cursor_pos)
            self.create_card_sprites()
            
        elif key == arcade.key.DOWN:
            self.cursor_pos = min(len(self.game_view.player_deck) - 1, self.cursor_pos + 1)
            if self.cursor_pos >= self.scroll_offset + self.visible_cards:
                self.scroll_offset = min(
                    len(self.game_view.player_deck) - self.visible_cards, 
                    self.cursor_pos - self.visible_cards + 1
                )
            self.create_card_sprites()
            
        elif key == arcade.key.LEFT:
            if self.scroll_offset > 0:
                self.scroll_offset -= 1
                self.create_card_sprites()
                
        elif key == arcade.key.RIGHT:
            if self.scroll_offset + self.visible_cards < len(self.game_view.player_deck):
                self.scroll_offset += 1
                self.create_card_sprites()
                
        elif key == arcade.key.ENTER:
            if self.selected_pos is None:
                self.selected_pos = self.cursor_pos
            else:
                # Swap cards
                self.game_view.player_deck[self.selected_pos], self.game_view.player_deck[self.cursor_pos] = (
                    self.game_view.player_deck[self.cursor_pos], self.game_view.player_deck[self.selected_pos]
                )
                self.selected_pos = None
            self.create_card_sprites()
            
        elif key == arcade.key.P:
            # Return to game view
            self.window.show_view(self.game_view)