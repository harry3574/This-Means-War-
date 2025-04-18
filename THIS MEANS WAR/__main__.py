import arcade
from views.game_view import GameView

def main():
    window = arcade.Window(1024, 768, "War Card Game")
    game_view = GameView()
    window.show_view(game_view)
    arcade.run()

if __name__ == "__main__":
    main()