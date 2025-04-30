# /views/delete_view.py
import arcade
from typing import List, Dict
from utils.saves import GameSaver
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT

class DeleteView(arcade.View):
    def __init__(self, delete_type: str = "profile"):
        super().__init__()
        self.saver = GameSaver()
        self.delete_type = delete_type  # "profile" or "save"
        self.items: List[Dict] = []
        self.selected_index = 0
        self.refresh_items()
        
        # UI configuration
        self.title_font_size = 36
        self.item_font_size = 24
        self.instruction_font_size = 18
        self.spacing = 50

    def refresh_items(self):
        """Load either profiles or saves based on delete_type"""
        if self.delete_type == "profile":
            self.items = self.saver.list_profiles()
        else:
            self.items = self.saver.list_saves()

    def on_show_view(self):
        """Called when view is shown"""
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.refresh_items()

    def on_draw(self):
        self.clear()
        
        # Title
        title = f"DELETE {self.delete_type.upper()}S"
        arcade.draw_text(
            title,
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - 70,
            arcade.color.RED,
            self.title_font_size,
            anchor_x="center",
            bold=True
        )

        # Items list
        start_y = SCREEN_HEIGHT - 150
        for i, item in enumerate(self.items):
            y_pos = start_y - i * self.spacing

            # Highlight selected item
            if i == self.selected_index:
                highlight_rect = arcade.rect.XYWH(
                    SCREEN_WIDTH // 2 - (SCREEN_WIDTH * 0.7) // 2,
                    y_pos - 20,
                    SCREEN_WIDTH * 0.7,
                    40
                )
                arcade.draw_rect_filled(highlight_rect, (100, 0, 0, 150))
            
            # Display item info
            if self.delete_type == "profile":
                text = f"{item['emoji']} {item['name']} (Saves: {item.get('save_count', 0)})"
            else:
                text = f"{item['save_name']} ({item['timestamp'][:16]})"
            
            arcade.draw_text(
                text,
                SCREEN_WIDTH // 2,
                y_pos,
                arcade.color.WHITE,
                self.item_font_size,
                anchor_x="center",
                anchor_y="center"
            )

        # Instructions
        instructions = [
            "UP/DOWN: Select item",
            "ENTER: Delete selected",
            "P: Switch to Profiles",
            "S: Switch to Saves",
            "ESC: Back to Menu"
        ]
        
        for i, text in enumerate(instructions):
            arcade.draw_text(
                text,
                30,
                60 + i * 30,
                arcade.color.LIGHT_GRAY,
                self.instruction_font_size
            )


    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if key == arcade.key.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == arcade.key.DOWN:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)
        elif key == arcade.key.ENTER and self.items:
            self.delete_selected()
        elif key == arcade.key.P:
            self.delete_type = "profile"
            self.refresh_items()
            self.selected_index = 0
        elif key == arcade.key.S:
            self.delete_type = "save"
            self.refresh_items()
            self.selected_index = 0
        elif key == arcade.key.ESCAPE:
            # Use the window's view switching
            self.window.show_view("menu")

    def delete_selected(self):
        """Delete the currently selected item"""
        if not self.items:
            return
            
        item = self.items[self.selected_index]
        
        if self.delete_type == "profile":
            success = self.saver.delete_profile(item['id'])
        else:
            success = self.saver.delete_save(item['id'])
        
        if success:
            self.refresh_items()
            # Reset selection to prevent out-of-bounds
            self.selected_index = min(self.selected_index, len(self.items) - 1)