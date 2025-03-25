# views/profile_view.py
import arcade
import sqlite3
from utils.database import list_profiles, create_profile, delete_profile

class ProfileView(arcade.View):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.selected_index = 0
        self.input_mode = False
        self.input_text = ""
        self.load_profiles()
        self.setup_ui()

    def setup_ui(self):
        """Create all UI elements"""
        # Title
        self.title = arcade.Text(
            "SELECT PROFILE",
            self.window.width//2,
            self.window.height - 100,
            arcade.color.BLACK, 36,
            anchor_x="center",
            bold=True
        )
        
        # Profile list
        self.profile_texts = []
        for i, profile in enumerate(self.profiles):
            self.profile_texts.append(
                arcade.Text(
                    f"{profile[2]} {profile[1]} (War: 1, Skirmish: 1)",
                    self.window.width//2,
                    self.window.height - 200 - i*60,
                    arcade.color.BLACK, 24,
                    anchor_x="center"
                )
            )
        
        # Buttons
        button_y = 100
        self.create_button = arcade.Text(
            "[C] CREATE PROFILE",
            self.window.width//2 - 200,
            button_y,
            arcade.color.GREEN, 24,
            anchor_x="center"
        )
        
        self.select_button = arcade.Text(
            "[ENTER] SELECT",
            self.window.width//2,
            button_y,
            arcade.color.BLUE if self.profiles else arcade.color.GRAY,
            24,
            anchor_x="center"
        )
        
        self.delete_button = arcade.Text(
            "[D] DELETE",
            self.window.width//2 + 200,
            button_y,
            arcade.color.RED if self.profiles else arcade.color.GRAY,
            24,
            anchor_x="center"
        )
        
        self.quit_button = arcade.Text(
            "[Q] QUIT",
            self.window.width//2,
            50,
            arcade.color.BLACK, 24,
            anchor_x="center"
        )

    def load_profiles(self):
        """Load profiles from database"""
        try:
            self.profiles = list_profiles()
        except sqlite3.OperationalError:
            self.profiles = []

    def on_draw(self):
        self.clear(arcade.color.WHITE)
        
        # Draw title
        self.title.draw()
        
        # Draw profiles
        for i, text in enumerate(self.profile_texts):
            if i == self.selected_index:
                text.color = arcade.color.GOLD
            else:
                text.color = arcade.color.BLACK
            text.draw()
        
        # Draw buttons
        self.create_button.draw()
        self.select_button.draw()
        self.delete_button.draw()
        self.quit_button.draw()
        
        # Input mode
        if self.input_mode:
            self.draw_input_box()

    def draw_input_box(self):
        """Draw profile creation input"""
        arcade.draw_rectangle_filled(
            self.window.width//2,
            self.window.height//2,
            400, 80,
            arcade.color.LIGHT_GRAY
        )
        arcade.draw_text(
            "Enter profile name:",
            self.window.width//2,
            self.window.height//2 + 30,
            arcade.color.BLACK, 20,
            anchor_x="center"
        )
        arcade.draw_text(
            self.input_text,
            self.window.width//2,
            self.window.height//2 - 10,
            arcade.color.BLACK, 24,
            anchor_x="center"
        )

    def on_key_press(self, key, modifiers):
        if self.input_mode:
            self.handle_input_mode(key)
        else:
            self.handle_normal_mode(key)

    def handle_input_mode(self, key):
        """Handle key presses during profile creation"""
        if key == arcade.key.ENTER:
            if self.input_text.strip():
                create_profile(self.input_text.strip())
                self.load_profiles()
                self.setup_ui()
            self.input_mode = False
            self.input_text = ""
        elif key == arcade.key.BACKSPACE:
            self.input_text = self.input_text[:-1]
        elif key == arcade.key.ESCAPE:
            self.input_mode = False
            self.input_text = ""
        elif hasattr(key, 'char'):
            self.input_text += key.char

    def handle_normal_mode(self, key):
        """Handle key presses in normal mode"""
        # Navigation
        if key == arcade.key.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == arcade.key.DOWN:
            self.selected_index = min(len(self.profiles)-1, self.selected_index + 1)
        
        # Actions
        elif key == arcade.key.C:
            self.input_mode = True
            self.input_text = ""
        elif key == arcade.key.Q:
            arcade.exit()
        elif key == arcade.key.ENTER and self.profiles:
            self.select_profile()
        elif key == arcade.key.D and self.profiles:
            self.delete_profile()

    def select_profile(self):
        """Load the selected profile"""
        profile = self.profiles[self.selected_index]
        from views.menu_view import MenuView
        self.window.show_view(MenuView(profile[0]))

    def delete_profile(self):
        """Delete the selected profile"""
        profile_id = self.profiles[self.selected_index][0]
        delete_profile(profile_id)
        self.load_profiles()
        self.setup_ui()
        self.selected_index = min(self.selected_index, len(self.profiles)-1)