# select_profile_view.py
import arcade
from utils.database import get_all_profiles

class SelectProfileView(arcade.View):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu
        self.profiles = get_all_profiles()
        self.selected_index = 0
        
        self.profile_texts = [
            arcade.Text(
                f"{profile[2]} {profile[1]} (War {profile[3] or 1}, Skirmish {profile[4] or 1})",
                self.window.width // 2,
                self.window.height - 150 - i * 50,
                arcade.color.BLACK,
                24,
                anchor_x="center"
            )
            for i, profile in enumerate(self.profiles)
        ]

    def on_draw(self):
        self.clear(arcade.color.WHITE)
        
        arcade.Text(
            "Select Profile:",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.BLACK,
            30,
            anchor_x="center"
        ).draw()
        
        for i, text in enumerate(self.profile_texts):
            if i == self.selected_index:
                text.color = arcade.color.BLUE
            else:
                text.color = arcade.color.BLACK
            text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.selected_index = max(0, self.selected_index - 1)
        elif key == arcade.key.DOWN:
            self.selected_index = min(len(self.profiles) - 1, self.selected_index + 1)
        elif key == arcade.key.ENTER:
            self.main_menu.selected_profile_id = self.profiles[self.selected_index][0]
            self.main_menu.update_profile_display()
            self.window.show_view(self.main_menu)
        elif key == arcade.key.ESCAPE:
            self.window.show_view(self.main_menu)
    
    def format_profile_text(self, profile):
        """Format profile text with proper war/skirmish display"""
        profile_id, name, emoji, war, skirmish = profile
        war_display = war if war is not None else 1
        skirmish_display = skirmish if skirmish is not None else 0
        return f"{emoji} {name} (War {war_display}, Skirmish {skirmish_display})"