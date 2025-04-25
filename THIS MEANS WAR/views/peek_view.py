import arcade
from arcade import Text
from game.card import Card
from utils.constant import *

class PeekView(arcade.View):
    def __init__(self, game, window=None):
        super().__init__()
        self.game = game
        self.window = window
        self.selected_card_index = None
        self.card_back = arcade.load_texture(":resources:images/cards/cardBack_red2.png")
        self.row_height = 40  # Increased from 25 for better spacing
        self.card_width = 80
        self.card_height = 30  # Flatter cards for more vertical space
        self.font_size = 14
        self.hovered_card = None
        self.show_help = False
        
        # Enhanced color scheme
        self.color_strong_win = arcade.color.GREEN
        self.color_weak_win = arcade.color.LIME_GREEN
        self.color_neutral = arcade.color.LIGHT_GRAY
        self.color_weak_loss = arcade.color.ORANGE
        self.color_strong_loss = arcade.color.RED
        self.color_suit_boost = arcade.color.SKY_BLUE
        self.color_suit_penalty = arcade.color.LIGHT_SALMON
        
        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize all UI elements with better spacing"""
        # Main headers
        self.title = Text(
            "DECK STRATEGY OVERVIEW",
            SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40,
            arcade.color.GOLD, 22,
            anchor_x="center", font_name="Garamond"
        )
        
        # Column headers with explanations
        self.col_headers = [
            Text("YOUR CARD", 120, SCREEN_HEIGHT - 80, arcade.color.CYAN, 16, anchor_x="center"),
            Text("VS", SCREEN_WIDTH//2, SCREEN_HEIGHT - 80, arcade.color.WHITE, 16, anchor_x="center"),
            Text("ENEMY CARD", 400, SCREEN_HEIGHT - 80, arcade.color.ORANGE, 16, anchor_x="center"),
            Text("PREDICTION", 650, SCREEN_HEIGHT - 80, arcade.color.WHITE, 16, anchor_x="center"),
            Text("SUIT EFFECT", 850, SCREEN_HEIGHT - 80, arcade.color.WHITE, 16, anchor_x="center")
        ]
        
        # Control buttons
        self.buttons = {
            'back': Text("BACK (ESC)", SCREEN_WIDTH - 100, 40, arcade.color.WHITE, 16, anchor_x="center"),
            'help': Text("HELP (H)", SCREEN_WIDTH - 200, 40, arcade.color.WHITE, 16, anchor_x="center"),
            'swap': Text("SWAP SELECTED", SCREEN_WIDTH//2, 40, arcade.color.YELLOW, 16, anchor_x="center")
        }
        
        # Help information
        self.help_info = Text(
            "▲▲ Strong Win (+20+) | ▲ Good Win (+10-19) | ■ Neutral\n"
            "▼ Risky Loss (-10-19) | ▼▼ Bad Loss (-20+) | Color shows suit effect",
            SCREEN_WIDTH//2, 80,
            arcade.color.WHITE, 14,
            anchor_x="center", width=SCREEN_WIDTH-100, multiline=True
        )

    def on_draw(self):
        # Background with subtle grid lines
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT),
            arcade.color.DARK_SLATE_GRAY
        )
        
        # Draw column separators
        for x in [250, 500, 700]:
            arcade.draw_line(x, 100, x, SCREEN_HEIGHT-90, arcade.color.GRAY, 1)
        
        # Draw headers
        self.title.draw()
        for header in self.col_headers:
            header.draw()
        
        # Draw card matchups
        self._draw_matchups()
        
        # Draw controls
        self._draw_controls()
        
        # Help overlay if active
        if self.show_help:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH-100, 200),
                (0, 0, 50, 200)
            )
            self.help_info.draw()

    def _draw_matchups(self):
        """Draw all card matchups with clear spacing"""
        for i, (player_card, ai_card) in enumerate(zip(
            self.game.player_hand[:24],  # Limit to first 24 for space
            self.game.ai_hand[:24]
        )):
            y_pos = SCREEN_HEIGHT - 120 - (i * self.row_height)
            
            # Highlight selected/hovered rows
            if i == self.selected_card_index:
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(SCREEN_WIDTH/2, y_pos, SCREEN_WIDTH-100, self.row_height-5),
                    (50, 50, 0, 100)
                )
            elif i == self.hovered_card:
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(SCREEN_WIDTH/2, y_pos, SCREEN_WIDTH-100, self.row_height-5),
                    (25, 25, 25, 100)
                )
            
            # Player card
            self._draw_card(player_card, 120, y_pos, is_player=True)
            
            # VS separator
            arcade.draw_text(
                "vs", SCREEN_WIDTH//2, y_pos,
                arcade.color.LIGHT_GRAY, 14,
                anchor_x="center", anchor_y="center"
            )
            
            # Enemy card
            self._draw_card(ai_card, 400, y_pos, is_player=False)
            
            # Advantage prediction
            self._draw_prediction(player_card, ai_card, 650, y_pos)
            
            # Suit effect
            self._draw_suit_effect(player_card, ai_card, 850, y_pos)

    def _draw_card(self, card, x, y, is_player):
        """Draw a card with appropriate styling"""
        color = arcade.color.CYAN if is_player else arcade.color.ORANGE
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, self.card_width, self.card_height),
            color
        )
        arcade.draw_text(
            f"{card.value}{card.suit}", x, y,
            arcade.color.BLACK, self.font_size,
            anchor_x="center", anchor_y="center"
        )

    def _draw_prediction(self, player_card, ai_card, x, y):
        """Draw the advantage prediction with visual indicators"""
        player_pressure, ai_pressure = self.game.calculate_pressure(player_card, ai_card)
        net_pressure = player_pressure - ai_pressure
        
        # Determine advantage level
        if net_pressure >= 20:
            color = self.color_strong_win
            symbol = "▲▲"
            label = f"Strong +{net_pressure}"
        elif net_pressure >= 10:
            color = self.color_weak_win
            symbol = "▲"
            label = f"Good +{net_pressure}"
        elif net_pressure <= -20:
            color = self.color_strong_loss
            symbol = "▼▼"
            label = f"Bad {net_pressure}"
        elif net_pressure <= -10:
            color = self.color_weak_loss
            symbol = "▼"
            label = f"Risky {net_pressure}"
        else:
            color = self.color_neutral
            symbol = "■"
            label = f"Even {net_pressure}"
        
        # Draw prediction
        arcade.draw_text(
            f"{symbol} {label}", x, y,
            color, self.font_size,
            anchor_x="center", anchor_y="center"
        )

    def _draw_suit_effect(self, player_card, ai_card, x, y):
        """Show the suit advantage effect"""
        advantage = player_card.get_suit_advantage(ai_card.suit)
        
        if advantage > 1.0:
            color = self.color_suit_boost
            effect = f"Boost x{advantage:.1f}"
        elif advantage < 1.0:
            color = self.color_suit_penalty
            effect = f"Penalty x{advantage:.1f}"
        else:
            color = self.color_neutral
            effect = "Neutral"
        
        arcade.draw_text(
            effect, x, y,
            color, self.font_size,
            anchor_x="center", anchor_y="center"
        )

    def _draw_controls(self):
        """Draw control buttons"""
        # Back button
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH-100, 40, 120, 30),
            arcade.color.RED
        )
        self.buttons['back'].draw()
        
        # Help button
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH-200, 40, 120, 30),
            arcade.color.BLUE
        )
        self.buttons['help'].draw()
        
        # Swap button (only shown when card is selected)
        if self.selected_card_index is not None:
            arcade.draw_rect_filled(
                arcade.rect.XYWH(SCREEN_WIDTH//2, 40, 200, 30),
                arcade.color.DARK_YELLOW
            )
            self.buttons['swap'].draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Handle row hovering"""
        self.hovered_card = None
        for i in range(min(len(self.game.player_hand), 24)):
            y_pos = SCREEN_HEIGHT - 120 - (i * self.row_height)
            if 50 <= x <= SCREEN_WIDTH-50 and y_pos-self.row_height/2 <= y <= y_pos+self.row_height/2:
                self.hovered_card = i
                break

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse interactions"""
        # Back button handling - use window reference directly
        if (SCREEN_WIDTH-160 <= x <= SCREEN_WIDTH-40) and (25 <= y <= 55):
            if hasattr(self.window, 'show_view'):
                self.window.show_view("game")  # Use view name
            else:
                # Fallback if window reference isn't available
                arcade.get_window().show_view(self.previous_view)  # You'll need to store previous_view

        # Card selection
        for i in range(min(len(self.game.player_hand), 24)):
            y_pos = SCREEN_HEIGHT - 120 - (i * self.row_height)
            if 50 <= x <= SCREEN_WIDTH-50 and y_pos-self.row_height/2 <= y <= y_pos+self.row_height/2:
                if self.selected_card_index is None:
                    self.selected_card_index = i
                else:
                    # Swap cards if same card clicked twice
                    if self.selected_card_index == i:
                        self.selected_card_index = None
                    else:
                        self._swap_cards(self.selected_card_index, i)
                return
        
        if (SCREEN_WIDTH-260 <= x <= SCREEN_WIDTH-140) and (25 <= y <= 55):
            self.show_help = not self.show_help
        
        if self.selected_card_index is not None and (SCREEN_WIDTH//2-100 <= x <= SCREEN_WIDTH//2+100) and (25 <= y <= 55):
            self._prompt_swap()

    def _swap_cards(self, index1, index2):
        """Swap two cards in player's deck"""
        self.game.swap_player_cards(index1, index2)
        self.selected_card_index = None

    def _prompt_swap(self):
        """Show swap confirmation"""
        if self.selected_card_index is not None:
            # In a real implementation, you might show a dialog here
            # For now we'll just swap with the next card
            swap_with = min(self.selected_card_index + 1, len(self.game.player_hand)-1)
            self._swap_cards(self.selected_card_index, swap_with)

    def on_key_press(self, key, modifiers):
        """Handle keyboard shortcuts"""
        if key == arcade.key.ESCAPE:
            if hasattr(self.window, 'show_view'):
                self.window.show_view("game")
            else:
                arcade.get_window().show_view(self.previous_view)