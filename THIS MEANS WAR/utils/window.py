# /utils/window.py
import arcade
from views.game_view import GameView
from views.peek_view import PeekView
from views.profile_view import ProfileView
from views.menu_view import MenuView
from utils.constant import *

class WarGameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "War Game")
        self.views = {}
        self.setup_views()
        
    def setup_views(self):
        """Initialize all game views"""
        # Create view instances
        self.views["game"] = GameView()
        self.views["peek"] = PeekView(self.views["game"].game, self)
        self.views["profile"] = ProfileView()
        self.views["menu"] = MenuView()
        
        # Set window references
        for view in self.views.values():
            view.window = self
        
    def show_view(self, view_name: str):
        """Show a view by name"""
        try:
            view = self.views[view_name]
            super().show_view(view)
        except KeyError:
            print(f"Error: View '{view_name}' not found. Available views: {list(self.views.keys())}")
            arcade.exit()