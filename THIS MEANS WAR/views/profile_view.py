# /views/profile_view.py
import arcade
from typing import List, Dict
from utils.saves import GameSaver
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT
from datetime import datetime

class ProfileView(arcade.View):
    def __init__(self, must_create: bool = False):
        super().__init__()
        self.must_create = must_create
        self.saver = GameSaver()
        self.profiles: List[Dict] = []
        self.selected_index = 0
        self.new_profile_name = ""
        self.mode = "select"  # or "create"
        self.refresh_profiles()
        
        # Track key presses for text input
        self.keys_pressed = set()
        self.last_key_time = 0
        self.key_repeat_delay = 0.1  # seconds

    def refresh_profiles(self):
        """Reload profiles from database"""
        self.profiles = self.saver.list_profiles()

    def on_show_view(self):
        """Called when view is shown"""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.refresh_profiles()
        if not self.profiles and not self.must_create:
            self.mode = "create"

    def on_draw(self):
        # Title
        title = "CREATE PROFILE" if self.mode == "create" else "SELECT PROFILE"
        arcade.draw_text(
            title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 50,
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center"
        )

        # Profiles list
        if self.mode == "select":
            for i, profile in enumerate(self.profiles):
                y_pos = SCREEN_HEIGHT - 120 - i * 40
                color = arcade.color.GOLD if i == self.selected_index else arcade.color.WHITE
                
                arcade.draw_text(
                    f"{profile['emoji']} {profile['name']}",
                    SCREEN_WIDTH // 2,
                    y_pos,
                    color,
                    font_size=20,
                    anchor_x="center"
                )

        # New profile input
        if self.mode == "create":
            arcade.draw_text(
                "Enter Profile Name:",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 30,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center"
            )
            
            # Corrected rectangle drawing using lrbt method
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH // 2 - 200,
                right=SCREEN_WIDTH // 2 + 200,
                top=SCREEN_HEIGHT // 2 + 5,
                bottom=SCREEN_HEIGHT // 2 - 45,
                color=arcade.color.WHITE,
                border_width=2
            )
            
            arcade.draw_text(
                self.new_profile_name,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 20,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center",
                anchor_y="center"
            )

        # Instructions
        instructions = [
            "UP/DOWN: Select profile" if self.mode == "select" else "TYPE: Enter name",
            "ENTER: Confirm",
            "N: New profile" if self.mode == "select" else "ESC: Cancel"
        ]
        
        for i, text in enumerate(instructions):
            arcade.draw_text(
                text,
                20,
                40 + i * 30,
                arcade.color.LIGHT_GRAY,
                font_size=16
            )

    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        self.keys_pressed.add(key)
        
        # Immediate actions
        if key == arcade.key.ESCAPE and self.mode == "create":
            if not self.must_create:
                self.mode = "select"
        
        elif key == arcade.key.N and self.mode == "select":
            self.mode = "create"
            self.new_profile_name = ""
        
        elif key == arcade.key.ENTER:
            if self.mode == "select" and self.profiles:
                self.select_profile()
            elif self.mode == "create" and self.new_profile_name.strip():
                self.create_profile()
        
        elif key == arcade.key.BACKSPACE and self.mode == "create":
            self.new_profile_name = self.new_profile_name[:-1]

    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_update(self, delta_time):
        """Handle continuous key presses"""
        current_time = datetime.now().timestamp()
        
        # Arrow key navigation
        if arcade.key.UP in self.keys_pressed and self.mode == "select":
            if current_time - self.last_key_time > self.key_repeat_delay:
                self.selected_index = max(0, self.selected_index - 1)
                self.last_key_time = current_time
        
        elif arcade.key.DOWN in self.keys_pressed and self.mode == "select":
            if current_time - self.last_key_time > self.key_repeat_delay:
                self.selected_index = min(len(self.profiles) - 1, self.selected_index + 1)
                self.last_key_time = current_time
        
        # Text input handling
        if self.mode == "create":
            for key in self.keys_pressed:
                if hasattr(key, 'char') and key.char and key not in [arcade.key.ENTER, arcade.key.BACKSPACE]:
                    if current_time - self.last_key_time > self.key_repeat_delay:
                        self.new_profile_name += key.char
                        self.last_key_time = current_time

    def select_profile(self):
        """Set the selected profile as active"""
        profile = self.profiles[self.selected_index]
        self.saver.current_profile_id = profile["id"]
        self.window.show_view("menu")

    def create_profile(self):
        """Create new profile"""
        name = self.new_profile_name.strip()
        if not name:
            return
            
        success, message = self.saver.create_profile(name)
        if success:
            self.refresh_profiles()
            if self.must_create:
                self.select_profile()
            else:
                self.mode = "select"
                self.selected_index = 0
        else:
            # You could show this error on screen
            print(message)