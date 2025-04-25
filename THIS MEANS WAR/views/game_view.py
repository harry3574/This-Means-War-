import arcade
from game.war_game import WarGame
from utils.constant import *
from utils.saves import GameSaver

class GameView(arcade.View):
    def __init__(self, window=None):
        super().__init__()
        self.game = WarGame()
        self.window = window
        self.showing_battle = False
        self.player_card = None
        self.ai_card = None
        self.button_pressed = False
        self.card_back = arcade.load_texture(":resources:images/cards/cardBack_red2.png")
        self.battle_resolve_handler = None
        self.waiting_for_input = True
        # Load card fronts for better visuals
        self.card_fronts = self._load_card_textures()
        self.history_page = 0
        self.max_history_pages = 0

        
    def _load_card_textures(self):
        """Load card front textures for better visuals"""
        card_fronts = {}
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace']
        
        for suit in suits:
            for value in values:
                key = f"{value}_of_{suit}"
                try:
                    card_fronts[key] = arcade.load_texture(f":resources:images/cards/{key}.png")
                except:
                    # Fallback to blank card if texture not found
                    card_fronts[key] = None
        return card_fronts
    
    def _get_card_texture(self, card):
        """Get the appropriate texture for a card"""
        suit_map = {'♥': 'hearts', '♦': 'diamonds', '♣': 'clubs', '♠': 'spades'}
        value_map = {
            'J': 'jack', 'Q': 'queen', 'K': 'king', 'A': 'ace',
            '10': '10', '9': '9', '8': '8', '7': '7', '6': '6',
            '5': '5', '4': '4', '3': '3', '2': '2'
        }
        
        key = f"{value_map[card.value]}_of_{suit_map[card.suit]}"
        return self.card_fronts.get(key)

    def _draw_pressure_status(self):
        """Draw the pressure points for both players"""
        # Player pressure
        arcade.draw_text(
            f"PRESSURE: {self.game.player_pressure}",
            SCREEN_WIDTH/4, 100,
            arcade.color.CYAN, 24,
            align="center", anchor_x="center"
        )
        
        # AI pressure
        arcade.draw_text(
            f"PRESSURE: {self.game.ai_pressure}",
            3*SCREEN_WIDTH/4, 100,
            arcade.color.ORANGE, 24,
            align="center", anchor_x="center"
        )
    
        # Pressure difference indicator
        diff = self.game.player_pressure - self.game.ai_pressure
        if diff != 0:
            color = arcade.color.GREEN if diff > 0 else arcade.color.RED
            arcade.draw_text(
                f"{abs(diff)} {'Ahead' if diff > 0 else 'Behind'}",
                SCREEN_WIDTH/2, 70,
                color, 20,
                align="center", anchor_x="center"
            )

    def on_draw(self):
        
        # Draw background with side panels
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT),
            arcade.color.FOREST_GREEN
        )
        
        # Draw player side panel
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/4, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT),
            (50, 50, 70, 150)  # Semi-transparent dark blue
        )
        
        # Draw AI side panel
        arcade.draw_rect_filled(
            arcade.rect.XYWH(3*SCREEN_WIDTH/4, SCREEN_HEIGHT/2, SCREEN_WIDTH/2, SCREEN_HEIGHT),
            (70, 50, 50, 150)  # Semi-transparent dark red
        )
        
        # Draw player label
        arcade.draw_text(
            "YOUR CARDS",
            SCREEN_WIDTH/4, SCREEN_HEIGHT - 50,
            arcade.color.WHITE, 24,
            align="center", anchor_x="center"
        )
        
        # Draw AI label
        arcade.draw_text(
            "OPPONENT",
            3*SCREEN_WIDTH/4, SCREEN_HEIGHT - 50,
            arcade.color.WHITE, 24,
            align="center", anchor_x="center"
        )

        # Add pressure display
        self._draw_pressure_status()
        
        # Add discard pile counts
        arcade.draw_text(
            f"Discards: {len(self.game.player_discard)}",
            SCREEN_WIDTH/4, 180,
            arcade.color.LIGHT_GRAY, 16,
            align="center", anchor_x="center"
        )
        arcade.draw_text(
            f"Discards: {len(self.game.ai_discard)}",
            3*SCREEN_WIDTH/4, 180,
            arcade.color.LIGHT_GRAY, 16,
            align="center", anchor_x="center"
        )
        
        # Draw face-down cards (before battle)
        if not self.showing_battle:
            # Player's face-down card
            arcade.draw_texture_rect(
                self.card_back,
                arcade.rect.XYWH(SCREEN_WIDTH/4, 250, CARD_WIDTH, CARD_HEIGHT)
            )
            
            # AI's face-down card
            arcade.draw_texture_rect(
                self.card_back,
                arcade.rect.XYWH(3*SCREEN_WIDTH/4, 250, CARD_WIDTH, CARD_HEIGHT)
            )
        
        # Draw revealed cards (during battle)
        else:
            # Player's revealed card with texture if available
            if self.player_card:
                texture = self._get_card_texture(self.player_card)
                if texture:
                    arcade.draw_texture_rect(
                        texture,
                        arcade.rect.XYWH(SCREEN_WIDTH/4, 250, CARD_WIDTH, CARD_HEIGHT)
                    )
                else:
                    # Fallback to simple card
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(SCREEN_WIDTH/4, 250, CARD_WIDTH, CARD_HEIGHT),
                        arcade.color.WHITE
                    )
                    arcade.draw_text(
                        f"{self.player_card.value}{self.player_card.suit}",
                        SCREEN_WIDTH/4, 250,
                        arcade.color.BLACK, 20,
                        align="center", anchor_x="center", anchor_y="center"
                    )
            
            # AI's revealed card with texture if available
            if self.ai_card:
                texture = self._get_card_texture(self.ai_card)
                if texture:
                    arcade.draw_texture_rect(
                        texture,
                        arcade.rect.XYWH(3*SCREEN_WIDTH/4, 250, CARD_WIDTH, CARD_HEIGHT)
                    )
                else:
                    # Fallback to simple card
                    arcade.draw_rect_filled(
                        arcade.rect.XYWH(3*SCREEN_WIDTH/4, 250, CARD_WIDTH, CARD_HEIGHT),
                        arcade.color.WHITE
                    )
                    arcade.draw_text(
                        f"{self.ai_card.value}{self.ai_card.suit}",
                        3*SCREEN_WIDTH/4, 250,
                        arcade.color.BLACK, 20,
                        align="center", anchor_x="center", anchor_y="center"
                    )
        
        # Draw deck sizes as progress bars
        self._draw_deck_status()
        
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
        
        # Draw battle history in scrollable area
        self._draw_battle_history()
    
    def _draw_deck_status(self):
        """Draw visual representation of remaining cards"""
        max_cards = 24  # Starting hand size
        player_pct = len(self.game.player_hand) / max_cards
        ai_pct = len(self.game.ai_hand) / max_cards
        
        # Player deck status
        arcade.draw_rect_outline(
            arcade.rect.XYWH(SCREEN_WIDTH/4, 150, 200, 50),
            arcade.color.WHITE,
        )
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/4 - 100 + 100 * player_pct, 150, 200 * player_pct, 16),
            arcade.color.BLUE
        )
        arcade.draw_text(
            f"{len(self.game.player_hand)}/{max_cards}",
            SCREEN_WIDTH/4, 150,
            arcade.color.WHITE, 16,
            align="center", anchor_x="center", anchor_y="center"
        )
        
        # AI deck status
        arcade.draw_rect_outline(
            arcade.rect.XYWH(3 * SCREEN_WIDTH / 4, 150, 200, 20),
            arcade.color.WHITE,
        )
        arcade.draw_rect_filled(
            arcade.rect.XYWH(3 * SCREEN_WIDTH / 4 - 100 + 100 * ai_pct, 150, 200 * ai_pct, 16),
            arcade.color.RED
        )
        arcade.draw_text(
            f"{len(self.game.ai_hand)}/{max_cards}",
            3*SCREEN_WIDTH/4, 150,
            arcade.color.WHITE, 16,
            align="center", anchor_x="center", anchor_y="center"
        )
    
    def _draw_battle_history(self):
        # Calculate pages
        history = self.game.current_skirmish.battle_history
        items_per_page = 5
        self.max_history_pages = max(0, (len(history) - 1) // items_per_page)
        
        # Show current page
        start_idx = self.history_page * items_per_page
        page_history = history[start_idx:start_idx+items_per_page]
        
        # Add page controls
        if self.max_history_pages > 0:
            arcade.draw_text(
                f"Page {self.history_page+1}/{self.max_history_pages+1}",
                SCREEN_WIDTH//2, 350,
                arcade.color.WHITE, 14
            )
    
    def on_mouse_press(self, x, y, button, modifiers):
        # Check reveal button (only when cards are face-down)
        if (not self.showing_battle and not self.button_pressed and
            SCREEN_WIDTH/2 - 100 <= x <= SCREEN_WIDTH/2 + 100 and 
            75 <= y <= 125):
            self.reveal_cards()
        
        # Check peek button - FIXED: Create new PeekView instance
        elif (SCREEN_WIDTH - 250 <= x <= SCREEN_WIDTH - 50) and (25 <= y <= 75):
            self.window.show_view("peek")
    
    def on_key_press(self, key, modifiers):
        # Spacebar to reveal cards
        if key == arcade.key.SPACE and not self.showing_battle and not self.button_pressed:
            self.reveal_cards()
    
        if key == arcade.key.F5:  # Quick save
            saver = GameSaver()
            saver.save_game(self.game, "quicksave")
            
        elif key == arcade.key.F9:  # Quick load
            saver = GameSaver()
            loaded_game = saver.load_game("quicksave")
            if loaded_game:
                self.game = loaded_game
    
    def reveal_cards(self):
        """Handle card revealing logic"""
        if self.button_pressed or not self.waiting_for_input:
            return
            
        self.button_pressed = True
        self.waiting_for_input = False
        self.showing_battle = True
        
        # Get cards but DON'T resolve battle yet
        if self.game.player_hand:
            self.player_card = self.game.player_hand[0]
        if self.game.ai_hand:
            self.ai_card = self.game.ai_hand[0]
        
        # Schedule card reveal for 2 seconds
        self.battle_resolve_handler = arcade.schedule(self.resolve_and_continue, 2.0)


    def resolve_and_continue(self, delta_time):
        """Resolve the current cards and prepare for next round"""
        if self.battle_resolve_handler:
            arcade.unschedule(self.battle_resolve_handler)
        
        # Only resolve if we have cards
        if self.player_card and self.ai_card:
            # Remove the shown cards from hands
            if (self.player_card in self.game.player_hand and 
                self.ai_card in self.game.ai_hand):
                self.game.player_hand.remove(self.player_card)
                self.game.ai_hand.remove(self.ai_card)
            
            # Resolve just this single battle
            self.game.resolve_single_battle(self.player_card, self.ai_card)
        
        # Reset for next round
        self.showing_battle = False
        self.button_pressed = False
        self.player_card = None
        self.ai_card = None
        self.waiting_for_input = True
        
        if self.game.is_game_over():
            winner = self.game.get_winner()
            # self.window.show_view(ResultView(winner))
    
    def on_hide_view(self):
        """Clean up when view changes"""
        if self.battle_resolve_handler:
            arcade.unschedule(self.battle_resolve_handler)

    def continue_to_next_round(self):
        """Prepare for next round"""
        self.waiting_for_input = False
        self.button_pressed = False
        self.player_card = None
        self.ai_card = None

    def _draw_progress_info(self):
        """Display the current war/skirmish/hand progress"""
        war = self.game.current_war
        skirmish = self.game.current_skirmish
        
        # War progress
        arcade.draw_text(
            f"War: {war.player_war_pressure}-{war.ai_war_pressure} "
            f"(Skirmish {war.current_skirmish_index + 1}/3)",
            SCREEN_WIDTH/2, SCREEN_HEIGHT - 30,
            arcade.color.WHITE, 20,
            align="center", anchor_x="center"
        )
        
        # Skirmish progress and pressure
        if skirmish:
            arcade.draw_text(
                f"Hands: {skirmish.hands_played}/28 | "
                f"Pressure: {skirmish.player_skirmish_pressure}-{skirmish.ai_skirmish_pressure}",
                SCREEN_WIDTH/2, SCREEN_HEIGHT - 60,
                arcade.color.WHITE, 18,
                align="center", anchor_x="center"
            )
        
        # Current hand pressure if in battle
        if self.showing_battle and self.game.current_hand:
            hand = self.game.current_hand
            arcade.draw_text(
                f"Hand Pressure: +{hand.player_pressure}/-{hand.ai_pressure}",
                SCREEN_WIDTH/2, SCREEN_HEIGHT - 90,
                arcade.color.GOLD, 18,
                align="center", anchor_x="center"
            )

    def _draw_battle_history(self):
        """Draw scrollable battle history"""
        # History background
        arcade.draw_rect_filled(
            arcade.rect.XYWH(SCREEN_WIDTH/2, 400, SCREEN_WIDTH - 100, 150),
            (0, 0, 0, 150)
        )
        
        # Show history from current skirmish
        history = self.game.current_skirmish.battle_history[-5:] if self.game.current_skirmish else []
        
        for i, event in enumerate(history):
            color = (
                arcade.color.GREEN if "won" in event.lower() else
                arcade.color.RED if "lost" in event.lower() else
                arcade.color.YELLOW
            )
            arcade.draw_text(
                event,
                50, 480 - i * 30,
                color, 14
            )