import arcade
from utils.window import WarGameWindow

def main():
    window = WarGameWindow()
    window.show_view("game")
    arcade.run()

if __name__ == "__main__":
    main()