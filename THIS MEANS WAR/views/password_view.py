# views/password_view.py
import arcade
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT

class PasswordEntryView(arcade.View):
    def __init__(self, profile: dict, success_view: str):
        super().__init__()
        self.profile = profile
        self.success_view = success_view
        self.password = ""
        self.error_message = ""
        self.show_password = False
        self.cursor_blink = 0
        self.cursor_visible = True

    def on_draw(self):
        arcade.start_render()
        
        # Title
        arcade.draw_text(
            f"Enter Password for {self.profile['emoji']} {self.profile['name']}",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 100,
            arcade.color.WHITE,
            24,
            anchor_x="center"
        )
        
        # Password box
        arcade.draw_rectangle_outline(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            400,
            50,
            arcade.color.WHITE,
            2
        )
        
        # Display password or asterisks
        display_text = self.password if self.show_password else "*" * len(self.password)
        arcade.draw_text(
            display_text,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            arcade.color.WHITE,
            24,
            anchor_x="center",
            anchor_y="center"
        )
        
        # Cursor
        if self.cursor_visible:
            text_width = arcade.get_text_width(display_text, 24)
            arcade.draw_line(
                SCREEN_WIDTH // 2 + text_width // 2 + 5,
                SCREEN_HEIGHT // 2 - 15,
                SCREEN_WIDTH // 2 + text_width // 2 + 5,
                SCREEN_HEIGHT // 2 + 15,
                arcade.color.WHITE,
                2
            )
        
        # Instructions
        instructions = [
            "ENTER: Submit",
            "SHIFT: Show password",
            "ESC: Cancel"
        ]
        for i, text in enumerate(instructions):
            arcade.draw_text(
                text,
                SCREEN_WIDTH // 2,
                100 + i * 30,
                arcade.color.LIGHT_GRAY,
                18,
                anchor_x="center"
            )
        
        # Error message
        if self.error_message:
            arcade.draw_text(
                self.error_message,
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 70,
                arcade.color.RED,
                18,
                anchor_x="center"
            )

    def on_update(self, delta_time):
        self.cursor_blink += delta_time
        if self.cursor_blink > 0.5:
            self.cursor_blink = 0
            self.cursor_visible = not self.cursor_visible

    def on_key_press(self, key, modifiers):
        if key == arcade.key.BACKSPACE:
            self.password = self.password[:-1]
            self.cursor_visible = True
            self.cursor_blink = 0
        elif key == arcade.key.ENTER:
            self.verify_password()
        elif key == arcade.key.ESCAPE:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())
        elif key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self.show_password = True
        elif hasattr(key, "char") and key.char:
            self.password += key.char
            self.cursor_visible = True
            self.cursor_blink = 0

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LSHIFT or key == arcade.key.RSHIFT:
            self.show_password = False

    def verify_password(self):
        if self.window.saver.verify_profile_password(self.profile['id'], self.password):
            self.window.current_profile = self.profile
            self.window.saver.current_profile_id = self.profile['id']
            self.window.show_view(self.success_view)
        else:
            self.error_message = "Incorrect password!"
            self.password = ""