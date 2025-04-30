# /views/save_load_view.py
import arcade
from typing import Optional
from utils.constant import SCREEN_WIDTH, SCREEN_HEIGHT

class SaveLoadView(arcade.View):
    def __init__(self, game_view, mode: str = "save"):
        super().__init__()
        self.game_view = game_view
        self.mode = mode  # "save" or "load"
        self.save_name = ""
        self.selected_save = None
        self.saves = self.game_view.saver.list_saves()
        
        # UI configuration
        self.title_font_size = 30
        self.save_font_size = 20
        self.input_font_size = 24

    def on_draw(self):
        arcade.start_render()
        
        # Background
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT,
            (0, 0, 0, 200)  # Semi-transparent overlay
        )
        
        # Dialog box
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2,
            600, 400,
            arcade.color.DARK_SLATE_GRAY
        )
        
        # Title
        title = "SAVE GAME" if self.mode == "save" else "LOAD GAME"
        arcade.draw_text(
            title,
            SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150,
            arcade.color.WHITE,
            self.title_font_size,
            anchor_x="center"
        )
        
        if self.mode == "save":
            # Save name input
            arcade.draw_text(
                "Save Name:",
                SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 50,
                arcade.color.WHITE,
                self.input_font_size
            )
            
            arcade.draw_rectangle_outline(
                SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 50,
                300, 40,
                arcade.color.WHITE
            )
            
            arcade.draw_text(
                self.save_name,
                SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 50,
                arcade.color.WHITE,
                self.input_font_size,
                anchor_x="center",
                anchor_y="center"
            )
        else:
            # Save slots
            for i, save in enumerate(self.saves):
                y_pos = SCREEN_HEIGHT//2 + 100 - i * 50
                color = arcade.color.GOLD if save == self.selected_save else arcade.color.WHITE
                
                arcade.draw_text(
                    f"{save['save_name']} - {save['timestamp']}",
                    SCREEN_WIDTH//2, y_pos,
                    color,
                    self.save_font_size,
                    anchor_x="center"
                )
        
        # Buttons
        arcade.draw_rectangle_filled(
            SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 150,
            150, 40,
            arcade.color.RED
        )
        arcade.draw_text(
            "Cancel",
            SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 150,
            arcade.color.WHITE,
            self.input_font_size,
            anchor_x="center",
            anchor_y="center"
        )
        
        if (self.mode == "save" and self.save_name) or (self.mode == "load" and self.selected_save):
            arcade.draw_rectangle_filled(
                SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT//2 - 150,
                150, 40,
                arcade.color.GREEN
            )
            arcade.draw_text(
                "Confirm",
                SCREEN_WIDTH//2 + 100, SCREEN_HEIGHT//2 - 150,
                arcade.color.WHITE,
                self.input_font_size,
                anchor_x="center",
                anchor_y="center"
            )

    def on_mouse_press(self, x, y, button, modifiers):
        # Cancel button
        if (SCREEN_WIDTH//2 - 175 <= x <= SCREEN_WIDTH//2 - 25 and 
            SCREEN_HEIGHT//2 - 170 <= y <= SCREEN_HEIGHT//2 - 130):
            self.window.show_view(self.game_view)
        
        # Confirm button
        if (self.mode == "save" and self.save_name) or (self.mode == "load" and self.selected_save):
            if (SCREEN_WIDTH//2 + 25 <= x <= SCREEN_WIDTH//2 + 175 and 
                SCREEN_HEIGHT//2 - 170 <= y <= SCREEN_HEIGHT//2 - 130):
                if self.mode == "save":
                    self.game_view.saver.save_game(self.game_view.game, self.save_name)
                else:
                    loaded_game = self.game_view.saver.load_game(self.selected_save['id'])
                    if loaded_game:
                        self.game_view.game = loaded_game
                self.window.show_view(self.game_view)
        
        # Save slot selection
        if self.mode == "load":
            for i, save in enumerate(self.saves):
                y_pos = SCREEN_HEIGHT//2 + 100 - i * 50
                if (SCREEN_WIDTH//2 - 250 <= x <= SCREEN_WIDTH//2 + 250 and 
                    y_pos - 20 <= y <= y_pos + 20):
                    self.selected_save = save

    def on_key_press(self, key, modifiers):
        if self.mode == "save":
            if key == arcade.key.BACKSPACE:
                self.save_name = self.save_name[:-1]
            elif key == arcade.key.ENTER and self.save_name:
                self.game_view.saver.save_game(self.game_view.game, self.save_name)
                self.window.show_view(self.game_view)
            elif hasattr(key, 'char') and key.char:
                self.save_name += key.char
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.game_view)