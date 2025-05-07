# main.py
import arcade
from utils.window import WarGameWindow
from utils.saves import GameSaver

def main():
    window = WarGameWindow()
    
    # Check for existing profiles and load the most recently used
    saver = GameSaver()
    profiles = saver.list_profiles()
    
    if profiles:
        # Automatically select the most recently played profile
        window.current_profile = profiles[0]
        saver.current_profile_id = profiles[0]['id']
        window.show_view("menu")
    else:
        # No profiles exist, force creation
        window.show_view("profile")
        
    arcade.run()

if __name__ == "__main__":
    main()