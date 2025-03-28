import arcade
from views.menu_view import ProfileSelectionView
from utils.database import db
from constants import SCREEN_HEIGHT, SCREEN_WIDTH, SCREEN_TITLE

class WarGame(arcade.Window):
    def __init__(self):
        super().__init__(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
            title=SCREEN_TITLE
        )
        # Initialize database
        db._ensure_db_exists()
        
    def setup(self):
        self.show_view(ProfileSelectionView())

def main():
    window = WarGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()