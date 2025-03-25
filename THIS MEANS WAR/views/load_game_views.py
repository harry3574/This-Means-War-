# views/load_game_view.py
import arcade
from arcade import View
from utils.database import list_saves, load_game
from game.game_view import GameView
from views.menu_view import MenuView

class LoadGameView(View):
    def __init__(self, profile_id):
        super().__init__()
        self.profile_id = profile_id
        self.saves = list_saves(profile_id)
        self.selected_index = 0

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(
            "Select Save Game",
            self.window.width//2,
            self.window.height - 50,
            arcade.color.BLACK,
            36,
            anchor_x="center"
        )
        
        for i, save in enumerate(self.saves):
            color = arcade.color.BLUE if i == self.selected_index else arcade.color.BLACK
            arcade.draw_text(
                f"Save {save[0]}: Rounds {save[1]}",
                self.window.width//2,
                self.window.height - 150 - i*50,
                color,
                24,
                anchor_x="center"
            )

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == arcade.key.DOWN:
            self.selected_index = min(len(self.saves)-1, self.selected_index + 1)
        elif key == arcade.key.ENTER:
            save_id = self.saves[self.selected_index][0]
            loaded_state = load_game(self.profile_id, save_id)
            self.window.show_view(GameView(self.profile_id, loaded_state))
        elif key == arcade.key.ESCAPE:
            self.window.show_view(MenuView(self.profile_id))