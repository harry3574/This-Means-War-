import arcade
from utils.database import get_all_profiles, delete_profile

class DeleteProfileView(arcade.View):
    def __init__(self, main_menu):
        super().__init__()
        self.main_menu = main_menu
        self.profiles = get_all_profiles()
        self.selected_index = 0
        self.confirming = False
        
        # Create profile text objects
        self.profile_texts = [
            arcade.Text(
                f"{profile[2]} {profile[1]}",
                self.window.width // 2,
                self.window.height - 150 - i * 50,
                arcade.color.BLACK,
                24,
                anchor_x="center"
            )
            for i, profile in enumerate(self.profiles)
        ]
        
        # Confirmation prompt
        self.confirm_text = arcade.Text(
            "Confirm Deletion? (Y/N)",
            self.window.width // 2,
            self.window.height // 2 - 100,
            arcade.color.RED,
            30,
            anchor_x="center"
        )

    def on_draw(self):
        self.clear(arcade.color.WHITE)
        
        # Title
        arcade.Text(
            "Delete Profile",
            self.window.width // 2,
            self.window.height - 100,
            arcade.color.BLACK,
            36,
            anchor_x="center"
        ).draw()
        
        # Draw profiles
        for i, text in enumerate(self.profile_texts):
            if i == self.selected_index:
                text.color = arcade.color.RED if self.confirming else arcade.color.BLUE
            else:
                text.color = arcade.color.BLACK
            text.draw()
        
        # Draw confirmation if needed
        if self.confirming:
            self.confirm_text.draw()

    def on_key_press(self, key, modifiers):
        if self.confirming:
            if key == arcade.key.Y:
                # Delete the profile
                profile_id = self.profiles[self.selected_index][0]
                delete_profile(profile_id)
                self.profiles = get_all_profiles()
                self.selected_index = min(self.selected_index, len(self.profiles) - 1)
                self.confirming = False
                
                # Update profile texts
                self.profile_texts = [
                    arcade.Text(
                        f"{profile[2]} {profile[1]}",
                        self.window.width // 2,
                        self.window.height - 150 - i * 50,
                        arcade.color.BLACK,
                        24,
                        anchor_x="center"
                    )
                    for i, profile in enumerate(self.profiles)
                ]
                
            elif key == arcade.key.N:
                self.confirming = False
            elif key == arcade.key.ESCAPE:
                self.confirming = False
        else:
            if key == arcade.key.UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif key == arcade.key.DOWN:
                self.selected_index = min(len(self.profiles) - 1, self.selected_index + 1)
            elif key == arcade.key.ENTER and self.profiles:
                self.confirming = True
            elif key == arcade.key.ESCAPE:
                self.window.show_view(self.main_menu)