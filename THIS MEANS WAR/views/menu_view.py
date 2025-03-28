import arcade
from arcade import View, gui
from typing import List, Optional
import sqlite3
from utils.database import db, Profile, GameSave
from constants import *

UNICODE_FONT = "Unifont-JP"

class ProfileSelectionView(View):
    def __init__(self):
        super().__init__()
        self.manager = gui.UIManager()
        self.manager.enable()
        self.profiles: List[Profile] = []
        self.selected_profile: Optional[Profile] = None
        
        # Setup UI with proper layout
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        # Clear existing widgets
        self.manager.clear()
        
        # Main vertical layout
        self.v_box = gui.UIBoxLayout()
        
        # Title with spacing
        title = gui.UILabel(
            text="Select Profile", 
            font_size=24,
            font_name=UNICODE_FONT
        )
        self.v_box.add(title)
        self.v_box.add(gui.UISpace(height=20))  # Spacing
        
        # Profile buttons
        self.profiles = db.list_profiles()
        for profile in self.profiles:
            btn = gui.UIFlatButton(
                text=f"{profile.emoji} {profile.name}",
                width=300,
                height=40
            )
            btn.on_click = self._make_profile_handler(profile)
            self.v_box.add(btn)
            self.v_box.add(gui.UISpace(height=10))  # Spacing between buttons
            
        # New Profile button
        new_btn = gui.UIFlatButton(
            text="➕ New Profile",
            width=300,
            height=40
        )
        new_btn.on_click = self._on_new_profile  # Fixed method reference
        self.v_box.add(new_btn)
        self.v_box.add(gui.UISpace(height=20))  # Extra space before quit
        
        # Quit button
        quit_btn = gui.UIFlatButton(
            text="Exit",
            width=200,
            height=40
        )
        quit_btn.on_click = self._on_exit
        self.v_box.add(quit_btn)
        
        # Modern anchoring
        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

    def _make_profile_handler(self, profile: Profile):
        def handler(event):
            self.selected_profile = profile
            self._show_saves()
        return handler

    def _show_saves(self):
        """Transition to save selection view"""
        if self.selected_profile:
            save_view = SaveSelectionView(self.selected_profile)
            self.window.show_view(save_view)

    def _on_new_profile(self, event):
        """Handle new profile button click"""
        # Clear existing UI
        self.manager.clear()
        
        # Create input dialog
        input_box = gui.UIInputText(
            width=300,
            height=40,
            text_color=arcade.color.BLACK,
            font_name=UNICODE_FONT
        )
        
        # Horizontal layout for input and button
        dialog = gui.UIBoxLayout(vertical=False)
        dialog.add(input_box)
        dialog.add(gui.UISpace(width=10))
        
        submit_btn = gui.UIFlatButton(
            text="Create",
            width=100,
            height=40
        )
        submit_btn.on_click = lambda e: self._create_profile(input_box.text)
        dialog.add(submit_btn)
        
        # Add cancel button
        cancel_btn = gui.UIFlatButton(
            text="Cancel",
            width=100,
            height=40
        )
        cancel_btn.on_click = lambda e: self.setup_ui()  # Return to main menu
        dialog.add(gui.UISpace(width=10))
        dialog.add(cancel_btn)
        
        # Center the dialog
        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=dialog,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

    def _create_profile(self, name: str):
        """Handle profile creation"""
        if name.strip():
            try:
                profile = db.create_profile(name)
                self.setup_ui()  # Refresh UI
            except sqlite3.IntegrityError:
                error = gui.UIMessageBox(
                    width=300,
                    height=160,
                    message_text="Name already exists!",
                    buttons=["OK"]
                )
                anchor = gui.UIAnchorLayout()
                anchor.add(
                    child=error,
                    anchor_x="center",
                    anchor_y="center"
                )
                self.manager.add(anchor)

    def _on_exit(self, event):
        """Handle exit button click"""
        arcade.exit()

    def on_draw(self):
        self.clear()
        self.manager.draw()

def on_new_profile(self, event):
    """Input dialog for profile creation"""
    # Clear existing UI elements first
    self.manager.clear()
    
    # Create a vertical box for the dialog
    dialog_box = gui.UIBoxLayout(vertical=True)
    
    # Add title with spacing
    title_label = gui.UILabel(
        text="Create New Profile",
        font_size=18,
        font_name=UNICODE_FONT,
        align="center",
        width=300
    )
    dialog_box.add(title_label)
    dialog_box.add(gui.UISpace(height=10))  # Manual spacing
    
    # Input field
    input_box = gui.UIInputText(
        width=280,
        height=40,
        text_color=arcade.color.BLACK,
        font_name=UNICODE_FONT
    )
    dialog_box.add(input_box)
    dialog_box.add(gui.UISpace(height=10))  # Manual spacing
    
    # Horizontal box for buttons
    button_box = gui.UIBoxLayout(vertical=False)
    
    # Left spacer for centering
    button_box.add(gui.UISpace(width=50))
    button_box.add(gui.UISpace(width=50))  # Adjust as needed
    
    # Create button
    submit_btn = gui.UIFlatButton(
        text="Create",
        width=100,
        height=40
    )
    submit_btn.on_click = lambda e: self._create_profile(input_box.text)
    button_box.add(submit_btn)
    
    # Space between buttons
    button_box.add(gui.UISpace(width=20))
    
    # Cancel button
    cancel_btn = gui.UIFlatButton(
        text="Cancel",
        width=100,
        height=40
    )
    cancel_btn.on_click = lambda e: self.setup_ui()  # Return to main menu
    button_box.add(cancel_btn)
    
    dialog_box.add(button_box)
    
    # Create anchor layout
    anchor = gui.UIAnchorLayout()
    anchor.add(
        child=dialog_box,
        anchor_x="center",
        anchor_y="center"
    )
    
    self.manager.add(anchor)

    def _create_profile(self, name: str):
        """Handle profile creation with error feedback"""
        if name.strip():
            try:
                profile = db.create_profile(name)
                self.setup_ui()  # Refresh UI
            except sqlite3.IntegrityError:
                error = gui.UIMessageBox(
                    width=300,
                    height=160,
                    message_text="Name already exists!",
                    buttons=["OK"]
                )
                anchor = gui.UIAnchorLayout()
                anchor.add(
                    child=error,
                    anchor_x="center",
                    anchor_y="center"
                )
                self.manager.add(anchor)



class SaveSelectionView(View):
    def __init__(self, profile: Profile):
        super().__init__()
        self.profile = profile
        self.manager = gui.UIManager()
        self.manager.enable()
        self.setup_ui()

    def setup_ui(self):
        """Save selection UI"""
        self.manager.clear()
        
        self.v_box = gui.UIBoxLayout()
        
        # Profile header
        header = gui.UILabel(
            text=f"{self.profile.emoji} {self.profile.name}",
            font_size=24,
            font_name=UNICODE_FONT
        )
        self.v_box.add(header)
        self.v_box.add(gui.UISpace(height=20))
        
        # Save slots
        self.saves = db.list_saves(self.profile.id)
        if self.saves:
            for save in self.saves:
                btn_text = f"War {save.total_rounds//78 + 1} | Score: {save.player_score}-{save.enemy_score}"
                btn = gui.UIFlatButton(
                    text=btn_text,
                    width=400,
                    height=40
                )
                btn.on_click = self._make_save_handler(save.id)
                self.v_box.add(btn)
                self.v_box.add(gui.UISpace(height=10))
        else:
            no_saves = gui.UILabel(text="No saved games found")
            self.v_box.add(no_saves)
            self.v_box.add(gui.UISpace(height=20))
        
        # Action buttons
        new_btn = gui.UIFlatButton(
            text="🎮 New Game",
            width=400,
            height=40
        )
        new_btn.on_click = self.on_new_game
        self.v_box.add(new_btn)
        self.v_box.add(gui.UISpace(height=10))
        
        back_btn = gui.UIFlatButton(
            text="🔙 Back",
            width=200,
            height=40
        )
        back_btn.on_click = self.on_back
        self.v_box.add(back_btn)
        
        # Create anchor layout
        anchor = gui.UIAnchorLayout()
        anchor.add(
            child=self.v_box,
            anchor_x="center",
            anchor_y="center"
        )
        self.manager.add(anchor)

    def _make_save_handler(self, save_id: int):
        def handler(event):
            self.load_game(save_id)
        return handler

    def load_game(self, save_id: int):
        """Load game with proper view transition"""
        from views.game_view import GameView
        saved_state = db.load_game_state(self.profile.id, save_id)
        if saved_state:
            game_view = GameView()
            game_view.setup(saved_state)
            self.window.show_view(game_view)

    def on_new_game(self, event):
        """Start new game with clean state"""
        from views.game_view import GameView
        game_view = GameView()
        game_view.setup()
        self.window.show_view(game_view)

    def on_back(self, event):
        """Return to profile selection"""
        self.window.show_view(ProfileSelectionView())

    def on_draw(self):
        self.clear()  # Changed from arcade.start_render()
        self.manager.draw()