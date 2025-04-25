import arcade
from views.game_view import GameView
from views.peek_view import PeekView
from utils.constant import *

class WarGameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "War Game")
        self.views = {}
        self.setup_views()
        
    def setup_views(self):
        """Initialize all game views"""
        # Create GameView first without window reference
        self.views["game"] = GameView()
        """Initialize all game views"""
        # Create both views with proper references
        self.views["game"] = GameView(self)  # Pass window reference
        self.views["peek"] = PeekView(self.views["game"].game, self)  # Pass both game and window
        
    def show_view(self, view_name):
        """Show a view by name"""
        if view_name in self.views:
            super().show_view(self.views[view_name])
        else:
            print(f"Error: View '{view_name}' not found")