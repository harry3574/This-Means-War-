# views/game_over_view.py
import arcade
from arcade import View
from views.menu_view import MenuView

class GameOverView(View):
    def __init__(self, message, color, game_view):
        super().__init__()
        self.message = message
        self.color = color
        self.game_view = game_view
        self.timer = 3.0  # Show for 3 seconds
        
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(
            self.message,
            self.window.width//2,
            self.window.height//2,
            self.color,
            36,
            anchor_x="center"
        )
        
    def on_update(self, delta_time):
        self.timer -= delta_time
        if self.timer <= 0:
            self.window.show_view(MenuView(self.game_view.profile_id))