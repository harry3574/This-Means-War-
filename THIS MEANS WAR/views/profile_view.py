# /views/profile_view.py
import arcade
from typing import List, Dict
from utils.saves import GameSaver
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT
from datetime import datetime
from utils.cursor import BlinkingCursor


class ProfileView(arcade.View):
    def __init__(self, must_create: bool = False):
        super().__init__()
        self.must_create = must_create
        self.saver = GameSaver()
        self.profiles: List[Dict] = []
        self.selected_index = 0
        self.mode = "select"  # or "create"
        self.refresh_profiles()
        
        # Track key presses for text input
        self.keys_pressed = set()
        self.last_key_time = 0
        self.key_repeat_delay = 0.1  # seconds

        self.new_profile_name = ""
        self.new_profile_password = ""
        self.active_input = "name"  # Can be "name" or "password"
        self.show_password = False
        self.name_input_rect = None
        self.password_input_rect = None
        self.select_input_active = True  # Track if password box is active in select mode
        self.password_input = ""  # Make sure this is initialized
        self.error_message = ""

        self.cursor = BlinkingCursor(blink_rate=0.5)  # You can adjust blink_rate if you want


    def refresh_profiles(self):
        """Reload profiles from database with debug output"""
        print("\n[DEBUG] Attempting to load profiles...")
        try:
            self.profiles = self.saver.list_profiles()
            print(f"[DEBUG] Found {len(self.profiles)} profiles:")
            for i, profile in enumerate(self.profiles):
                print(f"  {i+1}. ID: {profile['id']}, Name: {profile['name']}, Emoji: {profile['emoji']}")
        except Exception as e:
            print(f"[ERROR] Failed to load profiles: {str(e)}")
            self.profiles = []

    def on_show_view(self):
        """Called when view is shown"""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        profile = getattr(self.window, 'current_profile', None)
        print(f"[DEBUG MENU] Profile at menu: {profile}")
        self.refresh_profiles()
        if not self.profiles and not self.must_create:
            self.mode = "create"

    def on_draw(self):
        self.clear()

        self.cursor.update()

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
            self.select_input_active = True
            start_y = content_top - 50
            for i, profile in enumerate(self.profiles):
                y_pos = start_y - i * 50
                if i == self.selected_index:
                    arcade.draw_lrbt_rectangle_filled(SCREEN_WIDTH//4 + 20, SCREEN_WIDTH*3//4 - 20, y_pos - 25, y_pos + 25, (100, 100, 50, 150))
                arcade.draw_text(f"{profile['emoji']} {profile['name']}", SCREEN_WIDTH // 2, y_pos,
                                 arcade.color.GOLD if i == self.selected_index else arcade.color.WHITE,
                                 24, anchor_x="center", anchor_y="center")

        elif self.mode == "password_prompt":
            center_y = SCREEN_HEIGHT // 2
            arcade.draw_text("Enter Password:", SCREEN_WIDTH // 2, center_y + 60, arcade.color.WHITE, 24, anchor_x="center")
            arcade.draw_lrbt_rectangle_filled(SCREEN_WIDTH//2 - 210, SCREEN_WIDTH//2 + 210, center_y - 30, center_y + 30, (30, 30, 40))
            arcade.draw_lrbt_rectangle_outline(SCREEN_WIDTH//2 - 200, SCREEN_WIDTH//2 + 200, center_y - 20, center_y + 20, arcade.color.WHITE, 2)
            display_pw = self.password_input if self.show_password else "*" * len(self.password_input)
            arcade.draw_text(display_pw, SCREEN_WIDTH // 2, center_y, arcade.color.WHITE, 24, anchor_x="center", anchor_y="center")

        elif self.mode == "create":
            # Create profile form (middle layer)
            center_y = content_top - (content_top - content_bottom) // 2
            
            # Name Input
            arcade.draw_text(
                "Enter Profile Name:",
                SCREEN_WIDTH // 2,
                center_y + 100,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center"
            )
            
            # Name Input Box
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH//2 - 210,
                right=SCREEN_WIDTH//2 + 210,
                bottom=center_y + 10,
                top=center_y + 70,
                color=(30, 30, 40)
            )
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH//2 - 200,
                right=SCREEN_WIDTH//2 + 200,
                bottom=center_y + 20,
                top=center_y + 60,
                color=arcade.color.WHITE,
                border_width=2
            )
            arcade.draw_text(
                self.new_profile_name,
                SCREEN_WIDTH // 2,
                center_y + 50,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Draw blinking cursor for Name input if active input is "name"
            if self.active_input == "name" and self.cursor.visible:
                text_obj = arcade.Text(self.new_profile_name, 0, 0, font_size=24)
                text_width = text_obj.content_width
                cursor_x = SCREEN_WIDTH // 2 + text_width // 2 + 5  # Small padding after text
                cursor_y_bottom = center_y + 35
                cursor_y_top = center_y + 65
                arcade.draw_line(
                    cursor_x, cursor_y_bottom,
                    cursor_x, cursor_y_top,
                    arcade.color.WHITE,
                    2
                )
            
            # Password Input
            arcade.draw_text(
                "Enter Password:",
                SCREEN_WIDTH // 2,
                center_y,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center"
            )
            
            # Password Input Box
            arcade.draw_lrbt_rectangle_filled(
                left=SCREEN_WIDTH//2 - 210,
                right=SCREEN_WIDTH//2 + 210,
                bottom=center_y - 90,
                top=center_y - 30,
                color=(30, 30, 40)
            )
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH//2 - 200,
                right=SCREEN_WIDTH//2 + 200,
                bottom=center_y - 80,
                top=center_y - 40,
                color=arcade.color.WHITE,
                border_width=2
            )
            
            # Show password as asterisks or plain text based on show_password flag
            display_password = self.new_profile_password if self.show_password else "*" * len(self.new_profile_password)
            arcade.draw_text(
                display_password,
                SCREEN_WIDTH // 2,
                center_y - 50,
                arcade.color.WHITE,
                font_size=24,
                anchor_x="center",
                anchor_y="center"
            )
            
            # Draw blinking cursor for Password input if active input is "password"
            if self.active_input == "password" and self.cursor.visible:
                text_obj = arcade.Text(display_password, 0, 0, font_size=24)
                text_width = text_obj.content_width
                cursor_x = SCREEN_WIDTH // 2 + text_width // 2 + 5  # Small padding after text
                cursor_y_bottom = center_y - 75
                cursor_y_top = center_y - 35
                arcade.draw_line(
                    cursor_x, cursor_y_bottom,
                    cursor_x, cursor_y_top,
                    arcade.color.WHITE,
                    2
                )
            
            # Password requirements hint
            arcade.draw_text(
                "(Must be at least 4 characters)",
                SCREEN_WIDTH // 2,
                center_y - 110,
                arcade.color.LIGHT_GRAY,
                font_size=16,
                anchor_x="center"
            )


    # ... (keep all other methods unchanged) ...

    def on_key_press(self, key, modifiers):
        # === Navigation ===
        if key == arcade.key.ESCAPE:
            if self.mode == "create":
                if not self.must_create:
                    self.mode = "select"
            elif self.mode == "password_prompt":
                self.mode = "select"
            else:
                from views.menu_view import MenuView
                self.window.show_view(MenuView())

        elif key == arcade.key.TAB:
            if self.mode == "create":
                self.active_input = "password" if self.active_input == "name" else "name"

        elif key == arcade.key.UP and self.mode == "select":
            self.selected_index = max(0, self.selected_index - 1)

        elif key == arcade.key.DOWN and self.mode == "select":
            self.selected_index = min(len(self.profiles) - 1, self.selected_index + 1)

        # === Action keys ===
        elif key == arcade.key.ENTER:
            if self.mode == "create":
                self.create_profile()
            elif self.mode == "select":
                self.password_input = ""
                self.error_message = ""
                self.mode = "password_prompt"
            elif self.mode == "password_prompt":
                self.select_profile()

        elif key == arcade.key.BACKSPACE:
            if self.mode == "create":
                if self.active_input == "name":
                    self.new_profile_name = self.new_profile_name[:-1]
                else:
                    self.new_profile_password = self.new_profile_password[:-1]
            elif self.mode == "password_prompt":
                self.password_input = self.password_input[:-1]

        # === Toggle password visibility (Ctrl + P) ===
        elif key == arcade.key.P and (modifiers & arcade.key.MOD_CTRL):
            self.show_password = not self.show_password


    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.mode == "create":
            if self.name_input_rect and self.name_input_rect.collides_with_point((x, y)):
                self.active_input = "name"
            elif self.password_input_rect and self.password_input_rect.collides_with_point((x, y)):
                self.active_input = "password"

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
        print("\n[DEBUG] Attempting to select profile...")
        
        if not self.profiles:
            print("[DEBUG] No profiles available")
            return False

        profile = self.profiles[self.selected_index]
        print(f"[DEBUG] Trying profile: {profile['name']} (ID: {profile['id']})")

        if not self.password_input:
            print("[DEBUG] No password entered")
            self.error_message = "Password required."
            return False

        print("[DEBUG] Verifying password...")
        if not self.saver.verify_profile_password(profile['id'], self.password_input):
            print("[DEBUG] Password verification failed")
            self.error_message = "Incorrect password."
            return False

        print("[DEBUG] Password verified successfully!")

        self.saver.current_profile_id = profile['id']
        self.window.current_profile = profile

        print(f"[DEBUG] Active profile set to: {profile['name']} (ID: {profile['id']})")

        if self.must_create:
            print("[DEBUG] Launching new game...")
            from views.game_view import GameView
            view = GameView(self.window)
            view.game.initialize_new_campaign()
            self.window.show_view(view)
        else:
            print("[DEBUG] Returning to menu...")
            from views.menu_view import MenuView

            # Replace the menu view with a fresh instance (profile is now updated)
            self.window.views["menu"] = MenuView()
            self.window.views["menu"].window = self.window  # set the window reference manually
            self.window.show_view("menu")
        return True


    def create_profile(self):
        """Create new profile with initial game state"""
        name = self.new_profile_name.strip()
        password = self.new_profile_password.strip()
        if not name:
            return
            
        success, message = self.saver.create_profile(name, password)
        if not success:
            print(message)
            return
            
        # Get the newly created profile
        self.refresh_profiles()
        new_profile = next((p for p in self.profiles if p['name'] == name), None)
        if not new_profile:
            return
            
        # Set as current profile
        self.saver.current_profile_id = new_profile['id']
        self.window.current_profile = new_profile
        
        # Create initial game state
        from game.war_game import WarGame
        from views.game_view import GameView
        
        # Create and save initial game
        game = WarGame()
        game.initialize_new_campaign()
        self.saver.save_game(game, "initial_save")
        
        if self.must_create:
            # Start game with this profile
            game_view = GameView(self.window)
            game_view.game = game
            self.window.show_view(game_view)
        else:
            self.mode = "select"
            self.selected_index = 0

    def on_text(self, text: str):
        if self.mode == "create":
            if self.active_input == "name" and len(self.new_profile_name) < 20:
                self.new_profile_name += text
            elif self.active_input == "password" and len(self.new_profile_password) < 20:
                self.new_profile_password += text
        elif self.mode == "password_prompt" and len(self.password_input) < 20:
            self.password_input += text  # This handles typing in password promptt
