# views/menu_view.py
import arcade
from arcade import View
import arcade
from arcade import View
from typing import Optional

class MenuView(View):
    def __init__(self, profile_id: int, profile_name: Optional[str] = None):
        """
        Initialize the main menu view
        Args:
            profile_id: The ID of the current player profile
            profile_name: Optional name for display purposes
        """
        super().__init__()
        self.profile_id = profile_id
        self.profile_name = profile_name
        self.selected_option = 0
        self.options = [
            "Start New Game",
            "Load Saved Game",
            "Game Statistics",
            "Return to Profiles"
        ]
        self.background = arcade.load_texture("resources/images/menu_bg.png")

    def on_draw(self):
        """Render the menu"""
        arcade.start_render()
        
        # Draw background
        arcade.draw_lrwh_rectangle_textured(
            0, 0,
            self.window.width, self.window.height,
            self.background
        )
        
        # Draw title
        title_y = self.window.height * 0.8
        arcade.draw_text(
            "War Card Game",
            self.window.width // 2,
            title_y,
            arcade.color.GOLD,
            54,
            anchor_x="center",
            font_name="Garamond"
        )
        
        # Draw profile info if available
        if self.profile_name:
            arcade.draw_text(
                f"Player: {self.profile_name}",
                self.window.width // 2,
                title_y - 60,
                arcade.color.WHITE,
                24,
                anchor_x="center"
            )
        
        # Draw menu options
        option_start_y = self.window.height * 0.5
        for i, option in enumerate(self.options):
            color = arcade.color.GOLD if i == self.selected_option else arcade.color.WHITE
            arcade.draw_text(
                option,
                self.window.width // 2,
                option_start_y - i * 50,
                color,
                32,
                anchor_x="center",
                font_name="Garamond"
            )

    def on_key_press(self, key: int, modifiers: int):
        """Handle key presses"""
        if key == arcade.key.UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == arcade.key.DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == arcade.key.ENTER:
            self.handle_menu_selection()
        elif key == arcade.key.ESCAPE:
            from .profile_view import ProfileView
            self.window.show_view(ProfileView())

    def handle_menu_selection(self):
        """Execute the selected menu option"""
        if self.selected_option == 0:  # New Game
            from .game_view import GameView
            self.window.show_view(GameView(self.profile_id))
        elif self.selected_option == 1:  # Load Game
            from .load_game_views import LoadGameView
            self.window.show_view(LoadGameView(self.profile_id))
        elif self.selected_option == 2:  # Statistics
            from .stats_view import StatsView
            self.window.show_view(StatsView(self.profile_id))
        elif self.selected_option == 3:  # Return to Profiles
            from .profile_view import ProfileView
            self.window.show_view(ProfileView())

    def on_show_view(self):
        """When view is shown"""
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)