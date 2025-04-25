# /views/menu_view.py
import datetime
import arcade
from utils.saves import GameSaver
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.saver = GameSaver()
        self.current_profile = None
        self.menu_options = [
            {"text": "New Game", "action": "new_game"},
            {"text": "Load Game", "action": "load_game"},
            {"text": "Change Profile", "action": "change_profile"},
            {"text": "Quit", "action": "quit"}
        ]
        self.selected_index = 0
        self.showing_load_menu = False
        self.saves_list = []
        self.load_selected_index = 0

        # UI Elements
        self.title = "THIS MEANS WAR"
        self.title_font_size = 48
        self.option_font_size = 32
        self.profile_font_size = 24
        self.title_y = SCREEN_HEIGHT - 150
        self.option_start_y = SCREEN_HEIGHT // 2
        self.option_spacing = 60

        self.saver = GameSaver()
        self.current_profile = None

        # Modified profile loading logic
        profiles = self.saver.list_profiles()
        if not profiles:  # If no profiles exist
            from views.profile_view import ProfileView
            self.window.show_view(ProfileView())
        else:
            self.current_profile = profiles[0]
            self.saver.current_profile_id = self.current_profile['id']

        # Load current profile if available
        profiles = self.saver.list_profiles()
        if profiles:
            self.current_profile = profiles[0]
            self.saver.current_profile_id = self.current_profile['id']

    def on_show_view(self):
        """Called when view is shown"""
        profiles = self.saver.list_profiles()
        if not profiles:
            # Schedule profile view for next frame
            arcade.schedule_once(lambda dt: self.window.show_view("profile"), 0.1)
        else:
            self.current_profile = profiles[0]
            self.saver.current_profile_id = self.current_profile['id']

    def on_draw(self):
        # Draw title
        arcade.draw_text(
            self.title,
            SCREEN_WIDTH // 2,
            self.title_y,
            arcade.color.GOLD,
            self.title_font_size,
            anchor_x="center",
            font_name="Garamond"
        )

        # Draw current profile info
        if self.current_profile:
            profile_text = f"Profile: {self.current_profile['emoji']} {self.current_profile['name']}"
            arcade.draw_text(
                profile_text,
                SCREEN_WIDTH // 2,
                self.title_y - 70,
                arcade.color.CYAN,
                self.profile_font_size,
                anchor_x="center"
            )

        # Draw main menu or load menu
        if self.showing_load_menu:
            self._draw_load_menu()
        else:
            self._draw_main_menu()

    def _draw_main_menu(self):
        """Draw the main menu options"""
        for i, option in enumerate(self.menu_options):
            color = arcade.color.GOLD if i == self.selected_index else arcade.color.WHITE
            arcade.draw_text(
                option["text"],
                SCREEN_WIDTH // 2,
                self.option_start_y - i * self.option_spacing,
                color,
                self.option_font_size,
                anchor_x="center"
            )

    def _draw_load_menu(self):
        """Draw the load game menu"""
        # Title
        arcade.draw_text(
            "Select Save to Load",
            SCREEN_WIDTH // 2,
            self.title_y - 50,
            arcade.color.WHITE,
            self.option_font_size,
            anchor_x="center"
        )

        # Save slots
        for i, save in enumerate(self.saves_list):
            y_pos = self.option_start_y - 50 - i * 40
            color = arcade.color.GOLD if i == self.load_selected_index else arcade.color.WHITE
            
            # Format save info
            save_date = datetime.strptime(save['timestamp'], "%Y-%m-%d %H:%M:%S").strftime("%m/%d %H:%M")
            save_text = f"{save['save_name']} ({save_date}) - {save['player_cards']} vs {save['ai_cards']} cards"

            arcade.draw_text(
                save_text,
                SCREEN_WIDTH // 2,
                y_pos,
                color,
                20,
                anchor_x="center"
            )

        # Back option
        arcade.draw_text(
            "<< Back",
            50,
            50,
            arcade.color.LIGHT_GRAY,
            20
        )

    def on_key_press(self, key, modifiers):
        if self.showing_load_menu:
            self._handle_load_menu_keys(key)
        else:
            self._handle_main_menu_keys(key)

    def _handle_main_menu_keys(self, key):
        """Handle key presses for main menu"""
        if key == arcade.key.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == arcade.key.DOWN:
            self.selected_index = min(len(self.menu_options) - 1, self.selected_index + 1)
        elif key == arcade.key.ENTER:
            self._execute_menu_action()
        elif key == arcade.key.ESCAPE:
            self.window.close()

    def _handle_load_menu_keys(self, key):
        """Handle key presses for load menu"""
        if key == arcade.key.UP:
            self.load_selected_index = max(0, self.load_selected_index - 1)
        elif key == arcade.key.DOWN:
            self.load_selected_index = min(len(self.saves_list) - 1, self.load_selected_index + 1)
        elif key == arcade.key.ENTER and self.saves_list:
            self._load_selected_save()
        elif key == arcade.key.ESCAPE or key == arcade.key.BACKSPACE:
            self.showing_load_menu = False
            self.load_selected_index = 0

    def _execute_menu_action(self):
        """Execute the selected menu action"""
        action = self.menu_options[self.selected_index]["action"]
        
        if action == "new_game":
            self._start_new_game()
        elif action == "load_game":
            self.showing_load_menu = True
            self.saves_list = self.saver.list_saves()
        elif action == "change_profile":
            from views.profile_view import ProfileView
            self.window.show_view(ProfileView())
        elif action == "quit":
            self.window.close()

    def _start_new_game(self):
        """Start a brand new game"""
        from views.game_view import GameView
        if not self.current_profile:
            from views.profile_view import ProfileView
            # Force creation with must_create=True
            self.window.show_view(ProfileView(must_create=True))
        return
            
        game_view = GameView()
        game_view.game.initialize_new_campaign()
        self.window.show_view(game_view)

    def _load_selected_save(self):
        """Load the selected save game"""
        from views.game_view import GameView
        if not self.saves_list:
            return
            
        selected_save = self.saves_list[self.load_selected_index]
        loaded_game = self.saver.load_game(selected_save['id'])
        
        if loaded_game:
            game_view = GameView()
            game_view.game = loaded_game
            self.window.show_view(game_view)

    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse clicks for buttons"""
        if self.showing_load_menu:
            # Check if back button was clicked
            if x < 100 and y < 100:
                self.showing_load_menu = False
            # Check if a save was clicked
            for i, save in enumerate(self.saves_list):
                save_y = self.option_start_y - 50 - i * 40
                if (SCREEN_WIDTH//2 - 200 <= x <= SCREEN_WIDTH//2 + 200 and 
                    save_y - 20 <= y <= save_y + 20):
                    self.load_selected_index = i
                    self._load_selected_save()
                    break
        else:
            # Check menu options
            for i, option in enumerate(self.menu_options):
                option_y = self.option_start_y - i * self.option_spacing
                if (SCREEN_WIDTH//2 - 100 <= x <= SCREEN_WIDTH//2 + 100 and 
                    option_y - 20 <= y <= option_y + 20):
                    self.selected_index = i
                    self._execute_menu_action()
                    break