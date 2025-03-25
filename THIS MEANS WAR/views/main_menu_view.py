import arcade
from utils.database import create_profile, delete_profile, get_profile_details, get_all_profiles
from views.create_profile_view import CreateProfileView
from views.delete_profile_view import DeleteProfileView
from views.select_profile_view import SelectProfileView

class MainMenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.selected_profile_id = None
        self.selected_option = 0
        self.profiles = []
        self.load_profiles()
        
        # UI Elements
        self.title = None
        self.options = []
        self.profile_display = None
        self.create_ui()

    def load_profiles(self):
        """Load all profiles from database"""
        self.profiles = get_all_profiles()
        if self.profiles and not self.selected_profile_id:
            self.selected_profile_id = self.profiles[0][0]

    def create_ui(self):
        """Initialize all UI elements"""
        # Title
        self.title = arcade.Text(
            "WAR GAME - MAIN MENU",
            self.window.width // 2,
            self.window.height - 50,
            arcade.color.BLACK,
            36,
            anchor_x="center"
        )
        
        # Menu Options
        self.options = [
            arcade.Text("1. Create New Profile", 100, 400, arcade.color.BLACK, 24),
            arcade.Text("2. Select Profile", 100, 350, arcade.color.BLACK, 24),
            arcade.Text("3. Delete Profile", 100, 300, arcade.color.BLACK, 24),
            arcade.Text("4. Quit Game", 100, 250, arcade.color.BLACK, 24)
        ]
        
        # Profile Display
        self.update_profile_display()

        
    def update_profile_display(self):
        """Update the profile info display with proper edge case handling"""
        if self.selected_profile_id:
            details = get_profile_details(self.selected_profile_id)
            if details:
                name, emoji, war, skirmish = details
                # Handle None/0 cases
                war_display = war if war is not None else 1
                skirmish_display = skirmish if skirmish is not None else 0
                
                text = f"Loaded Profile: {emoji} {name} (War {war_display}, Skirmish {skirmish_display})"
                self.profile_display = arcade.Text(
                    text,
                    self.window.width // 2,
                    150,
                    arcade.color.BLUE,
                    24,
                    anchor_x="center"
                )
        else:
            self.profile_display = arcade.Text(
                "No Profile Selected",
                self.window.width // 2,
                150,
                arcade.color.RED,
                24,
                anchor_x="center"
            )

    def on_draw(self):
        self.clear(arcade.color.WHITE)
        
        # Draw title
        self.title.draw()
        
        # Draw options
        for i, option in enumerate(self.options):
            if i == self.selected_option:
                option.color = arcade.color.BLUE
            else:
                option.color = arcade.color.BLACK
            option.draw()
        
        # Draw profile info
        if self.profile_display:
            self.profile_display.draw()
        
        # Draw instructions
        arcade.Text(
            "Use ↑↓ to navigate, ENTER to select, ESC to exit",
            self.window.width // 2,
            50,
            arcade.color.GRAY,
            18,
            anchor_x="center"
        ).draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif key == arcade.key.DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif key == arcade.key.ENTER:
            self.handle_option_selection()
        elif key == arcade.key.ESCAPE:
            arcade.exit()

    def handle_option_selection(self):
        if self.selected_option == 0:  # Create Profile
            self.window.show_view(CreateProfileView(self))
        elif self.selected_option == 1:  # Select Profile
            if self.profiles:
                self.window.show_view(SelectProfileView(self))
        elif self.selected_option == 2:  # Delete Profile
            if self.profiles:
                self.window.show_view(DeleteProfileView(self))
        elif self.selected_option == 3:  # Quit
            arcade.exit()

    def on_show_view(self):
        self.load_profiles()
        self.update_profile_display()