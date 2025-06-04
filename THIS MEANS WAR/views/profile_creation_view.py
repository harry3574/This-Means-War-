# views/profile_creation_view.py
import arcade
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.saves import GameSaver
from utils.cursor import BlinkingCursor

INPUT_WIDTH = 300
INPUT_HEIGHT = 40
FIELD_SPACING = 70

class ProfileCreationView(arcade.View):
    def __init__(self, must_create: bool = False):
        super().__init__()
        self.must_create = must_create
        self.name_input = ""
        self.password_input = ""
        self.confirm_input = ""
        self.current_field = "name"
        self.error_message = ""
        self.show_password = False
        self.saver = GameSaver()
        self.cursor = BlinkingCursor()
        self.field_positions = {
            "name": SCREEN_HEIGHT / 2 + FIELD_SPACING,
            "password": SCREEN_HEIGHT / 2,
            "confirm": SCREEN_HEIGHT / 2 - FIELD_SPACING
        }

    def on_text(self, text: str):
        self.add_char(text)

    def on_draw(self):
        self.clear()
        self.cursor.update()

        # Background panel
        panel_width = SCREEN_WIDTH - 100
        panel_height = 300
        panel_x = SCREEN_WIDTH / 2
        panel_y = SCREEN_HEIGHT / 2

        arcade.draw_lrbt_rectangle_outline(
            left=panel_x - panel_width / 2,
            right=panel_x + panel_width / 2,
            top=panel_y + panel_height / 2,
            bottom=panel_y - panel_height / 2,
            color=(0, 0, 0, 150)
        )

        # Title
        title = "CREATE PROFILE" if self.must_create else "NEW PROFILE"
        arcade.draw_text(
            title,
            SCREEN_WIDTH / 2,
            SCREEN_HEIGHT - 80,
            arcade.color.WHITE,
            36,
            anchor_x="center"
        )

        # Input fields
        fields = [
            ("Name:", self.name_input, "name"),
            ("Password:", self._obscure(self.password_input), "password"),
            ("Confirm Password:", self._obscure(self.confirm_input), "confirm")
        ]

        for label, value, field_name in fields:
            y = self.field_positions[field_name]
            is_active = self.current_field == field_name
            color = arcade.color.GOLD if is_active else arcade.color.WHITE

            # Label
            arcade.draw_text(
                label,
                SCREEN_WIDTH / 2 - 200,
                y - INPUT_HEIGHT / 2,
                color,
                20
            )

            # Input box with different border for active field
            border_width = 3 if is_active else 2
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH / 2,
                right=SCREEN_WIDTH / 2 + INPUT_WIDTH,
                top=y + INPUT_HEIGHT / 2,
                bottom=y - INPUT_HEIGHT / 2,
                color=color,
                border_width=border_width
            )

            # Text inside input
            text_x = SCREEN_WIDTH / 2 + 10  # Left-aligned with padding
            arcade.draw_text(
                value,
                text_x,
                y,
                color,
                20,
                anchor_y="center"
            )

            # Draw cursor if this is the active field
            if is_active and self.cursor.visible:
                text = arcade.Text(value, 0, 0, font_size=20)
                text_width = text.content_width
                cursor_x = text_x + text_width + 2
                arcade.draw_line(
                    cursor_x, y - 15,
                    cursor_x, y + 15,
                    color,
                    2
                )

        # Instructions
        instructions = [
            "TAB/SHIFT+TAB: Switch fields",
            "ENTER: Submit",
            "CTRL+P: Toggle password visibility",
            "ESC: Cancel" if not self.must_create else "",
            "UP/DOWN: Navigate fields"
        ]
        for i, text in enumerate(instructions):
            if text:
                arcade.draw_text(
                    text,
                    SCREEN_WIDTH / 2,
                    100 + i * 24,
                    arcade.color.LIGHT_GRAY,
                    16,
                    anchor_x="center"
                )

        # Error message
        if self.error_message:
            arcade.draw_text(
                self.error_message,
                SCREEN_WIDTH / 2,
                150,
                arcade.color.RED,
                18,
                anchor_x="center"
            )

    def _obscure(self, text):
        return text if self.show_password else "*" * len(text)

    def on_key_press(self, key, modifiers):
        # Field navigation
        if key == arcade.key.TAB:
            if modifiers & arcade.key.MOD_SHIFT:
                self.previous_field()
            else:
                self.next_field()
        elif key == arcade.key.UP:
            self.previous_field()
        elif key == arcade.key.DOWN:
            self.next_field()
        elif key == arcade.key.ENTER:
            self.create_profile()
        elif key == arcade.key.ESCAPE and not self.must_create:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())
        elif key == arcade.key.P and (modifiers & arcade.key.MOD_CTRL):
            self.show_password = not self.show_password
        elif key == arcade.key.BACKSPACE:
            self.delete_char()

    def next_field(self):
        fields = ["name", "password", "confirm"]
        index = fields.index(self.current_field)
        self.current_field = fields[(index + 1) % len(fields)]

    def previous_field(self):
        fields = ["name", "password", "confirm"]
        index = fields.index(self.current_field)
        self.current_field = fields[(index - 1) % len(fields)]

    def add_char(self, char):
        if self.current_field == "name":
            self.name_input += char
        elif self.current_field == "password":
            self.password_input += char
        elif self.current_field == "confirm":
            self.confirm_input += char
        self.validate_current_field()

    def delete_char(self):
        if self.current_field == "name":
            self.name_input = self.name_input[:-1]
        elif self.current_field == "password":
            self.password_input = self.password_input[:-1]
        elif self.current_field == "confirm":
            self.confirm_input = self.confirm_input[:-1]
        self.validate_current_field()

    def validate_current_field(self):
        if self.current_field == "name" and not self.name_input.strip():
            self.error_message = "Name cannot be empty!"
        elif self.current_field == "password" and len(self.password_input) < 4:
            self.error_message = "Password must be at least 4 characters!"
        elif self.current_field == "confirm" and self.password_input != self.confirm_input:
            self.error_message = "Passwords don't match!"
        else:
            self.error_message = ""

    def create_profile(self):
        if not self.name_input.strip():
            self.error_message = "Name cannot be empty!"
            return
        if len(self.password_input) < 4:
            self.error_message = "Password must be at least 4 characters!"
            return
        if self.password_input != self.confirm_input:
            self.error_message = "Passwords don't match!"
            return

        success, message = self.saver.create_profile(
            self.name_input, self.password_input
        )

        if success:
            profiles = self.saver.list_profiles()
            new_profile = next(p for p in profiles if p['name'] == self.name_input)
            self.saver.current_profile_id = new_profile['id']

            if self.must_create:
                from views.game_view import GameView
                game_view = GameView(self.window)
                game_view.game.initialize_new_campaign()
                self.window.show_view("game")
            else:
                self.window.show_view("menu")
        else:
            self.error_message = message
