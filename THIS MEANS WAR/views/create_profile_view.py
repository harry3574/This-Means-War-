import arcade
from utils.database import create_profile

class CreateProfileView(arcade.View):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu
        self.input_text = ""
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_blink_timer = 0
        
        # UI Elements
        self.title = arcade.Text(
            "Create New Profile",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.BLACK,
            36,
            anchor_x="center"
        )
        
        self.input_prompt = arcade.Text(
            "Enter profile name:",
            self.window.width // 2 - 200,
            self.window.height // 2 + 50,
            arcade.color.BLACK,
            24
        )
        
        self.input_display = arcade.Text(
            "",
            self.window.width // 2 - 200,
            self.window.height // 2,
            arcade.color.BLACK,
            24
        )
        
        self.instructions = arcade.Text(
            "ENTER: Confirm | ESC: Cancel | BACKSPACE: Delete | ARROWS: Move Cursor",
            self.window.width // 2,
            100,
            arcade.color.GRAY,
            18,
            anchor_x="center"
        )

    def on_draw(self):
        self.clear(arcade.color.WHITE)
        
        # Draw static elements
        self.title.draw()
        self.input_prompt.draw()
        self.instructions.draw()
        
        # Draw input text
        self.input_display.text = self.input_text
        self.input_display.draw()
        
        # Draw cursor if visible
        if self.cursor_visible:
            # Create temporary text to measure width
            temp_text = arcade.Text(
                self.input_text[:self.cursor_pos],
                self.input_display.x,
                self.input_display.y,
                arcade.color.BLACK,
                24
            )
            cursor_x = temp_text.x + temp_text.content_width
            
            arcade.draw_line(
                cursor_x, self.input_display.y - 5,
                cursor_x, self.input_display.y + 25,
                arcade.color.BLACK, 2
            )

    def on_update(self, delta_time):
        # Blink cursor every 0.5 seconds
        self.cursor_blink_timer += delta_time
        if self.cursor_blink_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_blink_timer = 0

    def on_key_press(self, key, modifiers):
        # Reset cursor visibility on any key press
        self.cursor_visible = True
        self.cursor_blink_timer = 0
        
        if key == arcade.key.ENTER:
            if self.input_text.strip():
                create_profile(self.input_text.strip())
                self.main_menu.load_profiles()
                self.window.show_view(self.main_menu)
        
        elif key == arcade.key.BACKSPACE:
            if self.cursor_pos > 0:
                self.input_text = self.input_text[:self.cursor_pos-1] + self.input_text[self.cursor_pos:]
                self.cursor_pos = max(0, self.cursor_pos - 1)
        
        elif key == arcade.key.LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        
        elif key == arcade.key.RIGHT:
            self.cursor_pos = min(len(self.input_text), self.cursor_pos + 1)
        
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
        
        elif key == arcade.key.HOME:
            self.cursor_pos = 0
        
        elif key == arcade.key.END:
            self.cursor_pos = len(self.input_text)

    def on_text(self, text):
        """Handle text input directly"""
        # Insert character at cursor position
        self.input_text = self.input_text[:self.cursor_pos] + text + self.input_text[self.cursor_pos:]
        self.cursor_pos += len(text)