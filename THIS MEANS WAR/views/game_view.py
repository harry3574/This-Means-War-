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
        self.button_pressed = False
        self.card_back = arcade.load_texture(":resources:images/cards/cardBack_red2.png")
        self.waiting_for_input = False  # New state variable
        
    def on_draw(self):
        
        # Draw background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT),
            arcade.color.FOREST_GREEN
        )
        
        # Draw face-down cards (before battle)
        if not self.showing_battle:
            # Player's face-down card
            arcade.draw_texture_rect(
                self.card_back,
                arcade.rect.XYWH(SCREEN_WIDTH/2 - 150, 250, CARD_WIDTH, CARD_HEIGHT)
            )
            
            # AI's face-down card
            arcade.draw_texture_rect(
                self.card_back,
                arcade.rect.XYWH(SCREEN_WIDTH/2 + 150, 250, CARD_WIDTH, CARD_HEIGHT)
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
        
        # Draw reveal button (only when cards are face-down and not waiting)
        if not self.showing_battle and not self.waiting_for_input:
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
        
        # Draw "Continue" button when waiting for next round input
        elif self.waiting_for_input:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(SCREEN_WIDTH/2, 100, 200, 50),
                arcade.color.GREEN
            )
            arcade.draw_text(
                "Continue (SPACE)",
                SCREEN_WIDTH/2, 100,
                arcade.color.WHITE, 20,
                align="center", anchor_x="center", anchor_y="center"
            )
        
        # Draw peek button (always available)
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
        # Check reveal button (when available)
        if (not self.showing_battle and not self.waiting_for_input and not self.button_pressed and
            SCREEN_WIDTH/2 - 100 <= x <= SCREEN_WIDTH/2 + 100 and 
            75 <= y <= 125):
            self.reveal_cards()
        
        # Check continue button (after battle)
        elif (self.waiting_for_input and
              SCREEN_WIDTH/2 - 100 <= x <= SCREEN_WIDTH/2 + 100 and 
              75 <= y <= 125):
            self.continue_to_next_round()
        
        # Check peek button
        elif (SCREEN_WIDTH - 250 <= x <= SCREEN_WIDTH - 50) and (25 <= y <= 75):
            self.window.show_view("PeekView")
    
    def on_key_press(self, key, modifiers):
        # Spacebar to reveal cards or continue
        if key == arcade.key.SPACE:
            if not self.showing_battle and not self.waiting_for_input and not self.button_pressed:
                self.reveal_cards()
            elif self.waiting_for_input:
                self.continue_to_next_round()
    
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
        self.waiting_for_input = True  # Now waiting for player to continue
        
        if self.game.is_game_over():
            winner = self.game.get_winner()
            # self.window.show_view(ResultView(winner))
    
    def continue_to_next_round(self):
        """Prepare for next round"""
        self.waiting_for_input = False
        self.button_pressed = False
        self.player_card = None
        self.ai_card = None