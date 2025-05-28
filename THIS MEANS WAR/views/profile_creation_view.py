# views/profile_creation_view.py
import arcade
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT
from utils.saves import GameSaver

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

    def on_draw(self):
        self.clear()

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

        base_y = SCREEN_HEIGHT / 2 + FIELD_SPACING
        for i, (label, value, field_name) in enumerate(fields):
            y = base_y - i * FIELD_SPACING
            color = arcade.color.GOLD if self.current_field == field_name else arcade.color.WHITE

            # Label
            arcade.draw_text(
                label,
                SCREEN_WIDTH / 2 - 200,
                y - INPUT_HEIGHT / 2,
                color,
                20
            )

            # Input box
            arcade.draw_lrbt_rectangle_outline(
                left=SCREEN_WIDTH / 2,
                right=SCREEN_WIDTH / 2 + INPUT_WIDTH,
                top=y + INPUT_HEIGHT / 2,
                bottom=y - INPUT_HEIGHT / 2,
                color=color,
                border_width=2
            )

            # Text inside input
            arcade.draw_text(
                value,
                SCREEN_WIDTH / 2 + INPUT_WIDTH / 2,
                y,
                color,
                20,
                anchor_x="center",
                anchor_y="center"
            )

        # Instructions
        instructions = [
            "TAB: Switch field",
            "ENTER: Submit",
            "SHIFT: Show passwords",
            "ESC: Cancel" if not self.must_create else ""
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
        if key == arcade.key.TAB:
            self.cycle_fields()
        elif key == arcade.key.ENTER:
            self.create_profile()
        elif key == arcade.key.ESCAPE and not self.must_create:
            from views.menu_view import MenuView
            self.window.show_view(MenuView())
        elif key == arcade.key.BACKSPACE:
            self.delete_char()
        elif key in [arcade.key.LSHIFT, arcade.key.RSHIFT]:
            self.show_password = True
        elif isinstance(key, int) and 32 <= key <= 126:
            self.add_char(chr(key))

    def on_key_release(self, key, modifiers):
        if key in [arcade.key.LSHIFT, arcade.key.RSHIFT]:
            self.show_password = False

    def cycle_fields(self):
        fields = ["name", "password", "confirm"]
        index = fields.index(self.current_field)
        self.current_field = fields[(index + 1) % len(fields)]

    def add_char(self, char):
        if self.current_field == "name":
            self.name_input += char
        elif self.current_field == "password":
            self.password_input += char
        elif self.current_field == "confirm":
            self.confirm_input += char

    def delete_char(self):
        if self.current_field == "name":
            self.name_input = self.name_input[:-1]
        elif self.current_field == "password":
            self.password_input = self.password_input[:-1]
        elif self.current_field == "confirm":
            self.confirm_input = self.confirm_input[:-1]

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
