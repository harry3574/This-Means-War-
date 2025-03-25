import arcade
from utils.database import initialize_database
from views.main_menu_view import MainMenuView

def main():
    # Initialize database
    initialize_database()
    
    # Create window
    window = arcade.Window(
        width=1280,
        height=720,
        title="War Game",
        resizable=False
    )
    arcade.set_background_color(arcade.color.WHITE)
    
    # Show main menu
    window.show_view(MainMenuView())
    arcade.run()

if __name__ == "__main__":
    main()