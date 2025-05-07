# /utils/window.py
import arcade
from views.game_view import GameView
from views.peek_view import PeekView
from views.profile_view import ProfileView
from views.menu_view import MenuView
from views.delete_view import DeleteView
from utils.constant import *

class WarGameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "War Game")
        self.views = {}
        self.setup_views()
        self.current_profile = None  # Add profile storage
        
    def setup_views(self):
        """Initialize all game views"""
        # Create view instances with window reference
        self.views["game"] = GameView(self)
        self.views["peek"] = PeekView(self.views["game"].game, self)
        self.views["profile"] = ProfileView()
        self.views["menu"] = MenuView()
        self.views["delete"] = DeleteView()
        self.views["save_load"] = None
        
        # Set window references
        for view in self.views.values():
            if hasattr(view, 'window'):
                view.window = self
        
    def show_view(self, view_name: str, *args, **kwargs):
        """Show a view by name with optional arguments"""
        try:
            # Special case for SaveLoadView which needs the game_view reference
            if view_name == "save_load" and self.views[view_name] is None:
                from views.save_load_view import SaveLoadView
                self.views[view_name] = SaveLoadView(self.views["game"], *args, **kwargs)
            
            view = self.views[view_name]
            super().show_view(view)
        except KeyError:
            available = list(self.views.keys())
            print(f"Error: View '{view_name}' not found. Available views: {available}")
            arcade.exit()