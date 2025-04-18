import arcade
from game.war_game import WarGame

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
CARD_WIDTH = 80
CARD_HEIGHT = 120

class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.game = WarGame()
        self.showing_battle = False
        self.player_card = None
        self.ai_card = None
        self.button_pressed = False  # To prevent multiple clicks
        self.card_back = arcade.load_texture(":resources:images/cards/cardBack_red2.png")  # Built-in card back
        
    def on_draw(self):
        
        # Draw background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT),
            arcade.color.FOREST_GREEN
        )
        
        # Draw face-down cards (before battle)
        if not self.showing_battle:
            # Player's face-down card (brown back)
            arcade.draw_texture_rect(
                SCREEN_WIDTH/2 - 150, 250, 
                CARD_WIDTH, CARD_HEIGHT,
                self.card_back
            )
            
            # AI's face-down card (brown back)
            arcade.draw_texture_rect(
                SCREEN_WIDTH/2 + 150, 250, 
                CARD_WIDTH, CARD_HEIGHT,
                self.card_back
            )
        
        # Draw revealed cards (during battle)
        else:
            # Player's revealed card
            arcade.draw_rect_filled(
                arcade.rect.XYWH(SCREEN_WIDTH/2 - 150, 250, CARD_WIDTH, CARD_HEIGHT),
                arcade.color.WHITE
            )
            arcade.draw_text(
                f"{self.player_card.value}{self.player_card.suit}",
                SCREEN_WIDTH/2 - 150, 250,
                arcade.color.BLACK, 20,
                align="center", anchor_x="center", anchor_y="center"
            )
            
            # AI's revealed card
            arcade.draw_rect_filled(
                arcade.rect.XYWH(SCREEN_WIDTH/2 + 150, 250, CARD_WIDTH, CARD_HEIGHT),
                arcade.color.WHITE
            )
            arcade.draw_text(
                f"{self.ai_card.value}{self.ai_card.suit}",
                SCREEN_WIDTH/2 + 150, 250,
                arcade.color.BLACK, 20,
                align="center", anchor_x="center", anchor_y="center"
            )
        
        # Draw reveal button (only when cards are face-down)
        if not self.showing_battle:
            button_color = arcade.color.RED if not self.button_pressed else arcade.color.DARK_RED
            arcade.draw_rect_filled(
                arcade.rect.XYWH(SCREEN_WIDTH/2, 100, 200, 50),
                button_color
            )
            arcade.draw_text(
                "Reveal Cards (SPACE)",
                SCREEN_WIDTH/2, 100,
                arcade.color.WHITE, 20,
                align="center", anchor_x="center", anchor_y="center"
            )
        
        # Draw peek button
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH - 150, 50, 200, 50),
            arcade.color.BLUE
        )
        arcade.draw_text(
            "Peek Hand",
            SCREEN_WIDTH - 150, 50,
            arcade.color.WHITE, 16,
            align="center", anchor_x="center", anchor_y="center"
        )
        
        # Draw card counts
        arcade.draw_text(
            f"Your cards: {len(self.game.player_hand)}",
            50, SCREEN_HEIGHT - 50,
            arcade.color.WHITE, 20
        )
        arcade.draw_text(
            f"AI cards: {len(self.game.ai_hand)}",
            SCREEN_WIDTH - 200, SCREEN_HEIGHT - 50,
            arcade.color.WHITE, 20
        )
        
        # Draw battle history (last 3 events)
        for i, event in enumerate(self.game.battle_history[-3:]):
            arcade.draw_text(
                event, 50, 400 + i * 30,
                arcade.color.WHITE, 16
            )
    
    def on_mouse_press(self, x, y, button, modifiers):
        # Check reveal button (only when cards are face-down)
        if (not self.showing_battle and not self.button_pressed and
            SCREEN_WIDTH/2 - 100 <= x <= SCREEN_WIDTH/2 + 100 and 
            75 <= y <= 125):
            self.reveal_cards()
        
        # Check peek button
        elif (SCREEN_WIDTH - 250 <= x <= SCREEN_WIDTH - 50) and (25 <= y <= 75):
            self.window.show_view("PeekView")
    
    def on_key_press(self, key, modifiers):
        # Spacebar to reveal cards
        if key == arcade.key.SPACE and not self.showing_battle and not self.button_pressed:
            self.reveal_cards()
    
    def reveal_cards(self):
        """Handle card revealing logic"""
        self.button_pressed = True
        self.player_card = self.game.player_hand[0] if self.game.player_hand else None
        self.ai_card = self.game.ai_hand[0] if self.game.ai_hand else None
        self.showing_battle = True
        
        # Schedule battle resolution after 2 seconds
        arcade.schedule(self.resolve_battle, 2.0)
    
    def resolve_battle(self, delta_time):
        """Resolve the battle after cards are revealed"""
        self.game.resolve_battle()
        self.showing_battle = False
        self.button_pressed = False
        
        if self.game.is_game_over():
            winner = self.game.get_winner()
            # self.window.show_view(ResultView(winner))