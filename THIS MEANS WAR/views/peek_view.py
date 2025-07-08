import arcade
from arcade import Text
from game.card import Card
from utils.constant import *
from utils.theme import get_color, set_theme

class PeekView(arcade.View):
    def __init__(self, game, window=None):
        super().__init__()
        self.game = game
        self.window = window
        self.selected_card_index = None
        self.card_back = arcade.load_texture(":resources:images/cards/cardBack_red2.png")
        
        self.hovered_card = None
        self.show_help = False
        self.last_selected_index = None
        self.primary_selected_index = None  # Track first selection
        self.secondary_selected_index = None  # Track current navigation

        self.top_visible_index = 0     # Index of the top card currently shown
        self.secondary_selected_index = 0  # Index of the cursor (selected row)

        self.START_Y = SCREEN_HEIGHT - 120

        set_theme("high")
        
        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize all UI elements with better spacing"""

         # Help section positioning constants
        self.help_top = SCREEN_HEIGHT - 80
        self.help_section_spacing = 40
        self.help_line_spacing = 30

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
        

        # Enhanced help information with visual scoring guide
        self.help_info = [
            # Title
            Text("CARD BATTLE GUIDE", SCREEN_WIDTH//2, self.help_top, 
                arcade.color.GOLD, 18, anchor_x="center", font_name="Garamond"),
            
            # Scoring system header
            Text("SCORING SYSTEM", SCREEN_WIDTH//2, self.help_top - self.help_section_spacing, 
                arcade.color.CYAN, 16, anchor_x="center"),

            # First scoring line - split into 3 parts
            Text("▲▲ +20+ pts", 
                SCREEN_WIDTH//2 - 120, self.help_top - self.help_section_spacing - self.help_line_spacing,
                color_strong_win, 14, anchor_x="center"),
            Text("▲ +10-19 pts", 
                SCREEN_WIDTH//2, self.help_top - self.help_section_spacing - self.help_line_spacing,
                color_weak_win, 14, anchor_x="center"),
            Text("■ Neutral (0-9)", 
                SCREEN_WIDTH//2 + 120, self.help_top - self.help_section_spacing - self.help_line_spacing,
                color_neutral, 14, anchor_x="center"),

            # Second scoring line - split into 2 parts
            Text("▼ -10-19 pts", 
                SCREEN_WIDTH//2 - 80, self.help_top - self.help_section_spacing - self.help_line_spacing*2,
                color_weak_loss, 14, anchor_x="center"),
            Text("▼▼ -20+ pts", 
                SCREEN_WIDTH//2 + 80, self.help_top - self.help_section_spacing - self.help_line_spacing*2,
                color_strong_loss, 14, anchor_x="center"),


            # Suit effect explanations
            Text("Beats next suit (x1.5 bonus)", 
                SCREEN_WIDTH//2, self.help_top - self.help_section_spacing*2 - self.help_line_spacing*4, 
                color_suit_boost, 14, anchor_x="center"),
            Text("Loses to previous suit (x0.5 penalty)", 
                SCREEN_WIDTH//2, self.help_top - self.help_section_spacing*2 - self.help_line_spacing*5, 
                color_suit_penalty, 14, anchor_x="center"),
            
            # Suit multipliers header
            Text("SUIT MULTIPLIERS", SCREEN_WIDTH//2, self.help_top - self.help_section_spacing*2 - self.help_line_spacing*2, 
                arcade.color.CYAN, 16, anchor_x="center"),

            # Individual suit relationship elements
            Text("♠", SCREEN_WIDTH // 2 - 160, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                get_color("suit_spade"), 22, anchor_x="center"),
            Text(">", SCREEN_WIDTH // 2 - 120, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                color_suit_boost, 20, anchor_x="center"),
            Text("♣", SCREEN_WIDTH // 2 - 80, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                get_color("suit_club"), 22, anchor_x="center"),
            Text(">", SCREEN_WIDTH // 2 - 40, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                color_suit_boost, 20, anchor_x="center"),
            Text("♦", SCREEN_WIDTH // 2, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                get_color("suit_diamond"), 22, anchor_x="center"),
            Text(">", SCREEN_WIDTH // 2 + 40, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                color_suit_boost, 20, anchor_x="center"),
            Text("♥", SCREEN_WIDTH // 2 + 80, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                get_color("suit_heart"), 22, anchor_x="center"),
            Text(">", SCREEN_WIDTH // 2 + 120, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                color_suit_boost, 20, anchor_x="center"),
            Text("♠", SCREEN_WIDTH // 2 + 160, (self.help_top - self.help_section_spacing * 2 - self.help_line_spacing * 3) - 6,
                get_color("suit_spade"), 22, anchor_x="center"),


            # Controls
            Text("CONTROLS", SCREEN_WIDTH//2, self.help_top - self.help_section_spacing*3 - self.help_line_spacing*5, 
                arcade.color.CYAN, 16, anchor_x="center"),
            Text("Arrows: Navigate • Enter: Select/Swap", 
                SCREEN_WIDTH//2, self.help_top - self.help_section_spacing*3 - self.help_line_spacing*6, 
                arcade.color.WHITE, 14, anchor_x="center"),
            Text("H: Toggle Help • ESC: Back", 
                SCREEN_WIDTH//2, self.help_top - self.help_section_spacing*3 - self.help_line_spacing*7, 
                arcade.color.WHITE, 14, anchor_x="center")
        ]

        # Calculate help panel dimensions based on content
        help_height = self.help_section_spacing*3 + self.help_line_spacing*7 + 50
        self.help_bg = arcade.SpriteSolidColor(SCREEN_WIDTH-100, help_height, arcade.color.DARK_SLATE_GRAY)
        self.help_bg.position = SCREEN_WIDTH//2, self.help_top - help_height//2 + 20

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

        # Draw scrollbar
        self._draw_scrollbar()
        
        # Help overlay if active
        if self.show_help:
            # Semi-transparent background
            
            arcade.draw_rect_filled(
                arcade.rect.XYWH(self.help_bg.center_x, self.help_bg.center_y, self.help_bg.width, self.help_bg.height),
                arcade.color.DARK_BLUE
            )
            
            # Draw border
            arcade.draw_rect_outline(
                arcade.rect.XYWH(self.help_bg.center_x, self.help_bg.center_y, self.help_bg.width, self.help_bg.height),
                arcade.color.GOLD, 2
            )
            
            # Draw all help text elements
            for text in self.help_info:
                text.draw()
            

    def _draw_matchups(self):
        """Draw all card matchups with clear spacing and persistent selection"""

        visible_range = range(self.top_visible_index, min(self.top_visible_index + visible_items_count, len(self.game.player_hand)))

        for draw_index, i in enumerate(visible_range):
            player_card = self.game.player_hand[i]
            ai_card = self.game.ai_hand[i]

            # Calculate y position with scroll
            y_pos = self.START_Y - draw_index * row_height  # ❗️FIXED positions

            # Skip drawing if completely off screen to optimize
            if y_pos < -row_height or y_pos > SCREEN_HEIGHT + row_height:
                continue
            
            # Highlight logic
            if i == self.primary_selected_index:
                # Primary selection (persistent until swap/cancel)
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(SCREEN_WIDTH/2, y_pos, SCREEN_WIDTH-100, row_height-5),
                    (100, 0, 100, 150)  # Purple for primary selection
                )
            elif i == self.secondary_selected_index:
                # Current navigation position
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(SCREEN_WIDTH/2, y_pos, SCREEN_WIDTH-100, row_height-5),
                    (50, 50, 0, 150)  # Yellow for current position
                )
            elif i == self.hovered_card:
                # Mouse hover effect
                arcade.draw_rect_filled(
                    arcade.rect.XYWH(SCREEN_WIDTH/2, y_pos, SCREEN_WIDTH-100, row_height-5),
                    (25, 25, 25, 100))
            
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

    def _draw_scrollbar(self):
        """Draws a vertical scrollbar on the right of the matchup list."""
        total_items = len(self.game.player_hand)

        if total_items <= visible_items_count:
            return  # No need for a scrollbar

        # Draw track
        arcade.draw_rect_filled(
            arcade.rect.XYWH(scrollbar_x, scrollbar_bottom + scrollbar_height/2, 8, scrollbar_height),
            arcade.color.GRAY
        )

        # Calculate thumb size and position
        thumb_height = max((visible_items_count / total_items) * scrollbar_height, 20)
        scroll_range = total_items - visible_items_count
        scroll_percent = self.top_visible_index / scroll_range if scroll_range else 0
        thumb_y = scrollbar_top - (scroll_percent * (scrollbar_height - thumb_height)) - thumb_height / 2

        # Draw thumb
        arcade.draw_rect_filled(
            arcade.rect.XYWH(scrollbar_x, thumb_y, 8, thumb_height),
            arcade.color.DARK_BLUE
        )
        arcade.draw_rect_filled(
            arcade.rect.XYWH(scrollbar_x, thumb_y, 8, thumb_height),
            arcade.color.GOLD
        )

    def _draw_card(self, card, x, y, is_player):
        """Draw a card with appropriate styling"""
        # Background color stays the same
        background_color = arcade.color.CYAN if is_player else arcade.color.ORANGE
        arcade.draw_rect_filled(
            arcade.rect.XYWH(x, y, card_width, card_height),
            background_color
        )

        # Get color from theme based on card suit
        suit_key = suit_map.get(card.suit, "text_primary")  # Fallback in case suit is invalid
        text_color = get_color(suit_key)

        # Draw the card text (value + suit) in themed color
        arcade.draw_text(
            f"{card.value}{card.suit}", x, y,
            text_color, font_size,
            anchor_x="center", anchor_y="center"
        )

    def _draw_prediction(self, player_card, ai_card, x, y):
        """Draw the advantage prediction with visual indicators"""
        player_pressure, ai_pressure = self.game.calculate_pressure(player_card, ai_card)
        net_pressure = player_pressure - ai_pressure
        
        # Determine advantage level
        if net_pressure >= 20:
            color = color_strong_win
            symbol = "▲▲"
            label = f"Strong +{net_pressure}"
        elif net_pressure >= 10:
            color = color_weak_win
            symbol = "▲"
            label = f"Good +{net_pressure}"
        elif net_pressure <= -20:
            color = color_strong_loss
            symbol = "▼▼"
            label = f"Bad {net_pressure}"
        elif net_pressure <= -10:
            color = color_weak_loss
            symbol = "▼"
            label = f"Risky {net_pressure}"
        else:
            color = color_neutral
            symbol = "■"
            label = f"Even {net_pressure}"
        
        # Draw prediction
        arcade.draw_text(
            f"{symbol} {label}", x-30, y,
            color, font_size,
            anchor_x="center", anchor_y="center"
        )

    def _draw_suit_effect(self, player_card, ai_card, x, y):
        """Show the suit advantage effect"""
        advantage = player_card.get_suit_advantage(ai_card.suit)
        
        if advantage > 1.0:
            color = color_suit_boost
            effect = f"Boost x{advantage:.1f}"
        elif advantage < 1.0:
            color = color_suit_penalty
            effect = f"Penalty x{advantage:.1f}"
        else:
            color = color_neutral
            effect = "Neutral"
        
        arcade.draw_text(
            effect, x, y,
            color, font_size,
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
            y_pos = SCREEN_HEIGHT - 120 - (i * row_height) - self.scroll_y
            if 50 <= x <= SCREEN_WIDTH-50 and y_pos-row_height/2 <= y <= y_pos+row_height/2:
                self.hovered_card = i
                break

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse interactions"""
        # Back button handling - use window reference directly
        if (SCREEN_WIDTH-160 <= x <= SCREEN_WIDTH-40) and (25 <= y <= 55):
            if hasattr(self.window, 'show_view'):
                self.window.show_view("game")
            else:
                # Fallback if window reference isn't available
                arcade.get_window().show_view(self.previous_view) 

        # Card selection
        for i in range(min(len(self.game.player_hand), 24)):
            y_pos = SCREEN_HEIGHT - 120 - (i * row_height) - self.scroll_y
            if 50 <= x <= SCREEN_WIDTH-50 and y_pos-row_height/2 <= y <= y_pos+row_height/2:
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

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Scroll through the list using the mouse wheel."""
        max_index = len(self.game.player_hand) - 1

        # Scroll up
        if scroll_y > 0:
            if self.secondary_selected_index > 0:
                self.secondary_selected_index -= 1
                if self.secondary_selected_index < self.top_visible_index:
                    self.top_visible_index = max(0, self.top_visible_index - 1)

        # Scroll down
        elif scroll_y < 0:
            if self.secondary_selected_index < max_index:
                self.secondary_selected_index += 1
                if self.secondary_selected_index >= self.top_visible_index + visible_items_count:
                    self.top_visible_index = min(
                        max_index - visible_items_count + 1,
                        self.top_visible_index + 1
                    )

    def _swap_cards(self, index1, index2):
        """Swap two cards in player's deck with validation"""
        if hasattr(self.game, 'swap_player_cards'):
            try:
                self.game.swap_player_cards(index1, index2)
                # Optional: Add visual feedback here
                swap_sound
            except Exception as e:
                print(f"Error swapping cards: {e}")
        else:
            print("Game instance doesn't support card swapping")
        self.selected_card_index = None

    def _prompt_swap(self):
        """Show swap confirmation"""
        if self.selected_card_index is not None:
            # In a real implementation, you might show a dialog here
            # For now we'll just swap with the next card
            swap_with = min(self.selected_card_index + 1, len(self.game.player_hand)-1)
            self._swap_cards(self.selected_card_index, swap_with)

    def on_key_press(self, key, modifiers):
        """Handle keyboard shortcuts and navigation"""
        # Existing ESC and H key handling
        if key == arcade.key.ESCAPE:
            if hasattr(self.window, 'show_view'):
                self.window.show_view("game")
            else:
                arcade.get_window().show_view(self.previous_view)
            return
        
        if key == arcade.key.H:
            self.show_help = not self.show_help
            return
        
        max_index = min(len(self.game.player_hand), 24) - 1
        
        if key == arcade.key.UP:
            if self.secondary_selected_index > 0:
                self.secondary_selected_index -= 1

                if self.secondary_selected_index < self.top_visible_index:
                    self.top_visible_index -= 1


        elif key == arcade.key.DOWN:
            if self.secondary_selected_index < len(self.game.player_hand) - 1:
                self.secondary_selected_index += 1

                if self.secondary_selected_index >= self.top_visible_index + visible_items_count:
                    self.top_visible_index += 1
        
        elif key == arcade.key.ENTER or key == arcade.key.SPACE:
            # Select or swap cards
            if self.secondary_selected_index is not None:
                if self.primary_selected_index is None:
                    # First selection
                    self.primary_selected_index = self.secondary_selected_index
                    select_sound
                else:
                    # Perform swap
                    self._swap_cards(self.primary_selected_index, self.secondary_selected_index)
                    self.primary_selected_index = None
                    self.secondary_selected_index = None
        
        elif key == arcade.key.LEFT:
            # Jump to first card
            self.secondary_selected_index = 0
        
        elif key == arcade.key.RIGHT:
            # Jump to last card
            self.secondary_selected_index = max_index
        
        elif key == arcade.key.ESCAPE:
            # Cancel all selections
            self.primary_selected_index = None
            self.secondary_selected_index = None

    def clamp_scroll(self):
        max_scroll = max(0, len(self.game.player_hand) * row_height - (SCREEN_HEIGHT - 200))
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))
