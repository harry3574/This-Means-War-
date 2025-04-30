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
        self.clear()

        # Draw the background first
        arcade.draw_lrbt_rectangle_filled(
            left=0,
            right=SCREEN_WIDTH,
            bottom=0,
            top=SCREEN_HEIGHT,
            color=arcade.color.DARK_SLATE_GRAY
        )

        # Title (top layer)
        title = "CREATE PROFILE" if self.mode == "create" else "SELECT PROFILE"
        arcade.draw_text(
            title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,  # Lowered slightly
            arcade.color.WHITE,
            font_size=30,
            anchor_x="center",
            bold=True
        )

        # Main content area
        content_top = SCREEN_HEIGHT - 100
        content_bottom = 100

        # Draw a semi-transparent panel for the content
        arcade.draw_lrbt_rectangle_filled(
            left=SCREEN_WIDTH//4,
            right=SCREEN_WIDTH*3//4,
            bottom=content_bottom,
            top=content_top,
            color=(50, 50, 70, 200)
        )

        if self.mode == "select":
            # Profile list (middle layer)
            start_y = content_top - 50
            for i, profile in enumerate(self.profiles):
                y_pos = start_y - i * 50
                
                # Highlight selected profile
                if i == self.selected_index:
                    arcade.draw_lrbt_rectangle_filled(
                        left=SCREEN_WIDTH//4 + 20,
                        right=SCREEN_WIDTH*3//4 - 20,
                        bottom=y_pos - 25,
                        top=y_pos + 25,
                        color=(100, 100, 50, 150)
                    )
                
                arcade.draw_text(
                    f"{profile['emoji']} {profile['name']}",
                    SCREEN_WIDTH // 2,
                    y_pos,
                    arcade.color.GOLD if i == self.selected_index else arcade.color.WHITE,
                    font_size=24,
                    anchor_x="center",
                    anchor_y="center"
                )

        elif self.mode == "create":
            # Create profile form (middle layer)
            center_y = content_top - (content_top - content_bottom) // 2
            
            # Input label
            arcade.draw_text(
                "Enter Profile Name:",
                SCREEN_WIDTH // 2,
                center_y + 60,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center"
            )
            
            # Input box background
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH//2 - 210,
                right=SCREEN_WIDTH//2 + 210,
                bottom=center_y - 50,
                top=center_y + 10,
                color=(30, 30, 40)
            )
            
            # Input box outline
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH//2 - 200,
                right=SCREEN_WIDTH//2 + 200,
                bottom=center_y - 40,
                top=center_y,
                color=arcade.color.WHITE,
                border_width=2
            )
            
            # Input text
            arcade.draw_text(
                self.new_profile_name,
                SCREEN_WIDTH // 2,
                center_y - 20,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center",
                anchor_y="center"
            )

        # Instructions (top layer)
        instructions = [
            "UP/DOWN: Select profile" if self.mode == "select" else "TYPE: Enter name",
            "ENTER: Confirm",
            "N: New profile" if self.mode == "select" else "ESC: Cancel"
        ]
        
        arcade.draw_text(
            "\n".join(instructions),
            30,
            60,
            arcade.color.LIGHT_GRAY,
            font_size=18,
            multiline=True,
            width=SCREEN_WIDTH - 60
        )

    # ... (keep all other methods unchanged) ...

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

    def on_text(self, text: str):
        if self.mode == "create" and len(self.new_profile_name) < 20:
            self.new_profile_name += text
            self.cursor_visible = True
            self.cursor_blink = 0