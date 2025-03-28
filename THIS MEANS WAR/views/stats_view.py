import arcade
from arcade import View, gui
from game.game_state import WarGameState
from constants import *

class StatsView(View):
    def __init__(self, game_state: WarGameState):
        super().__init__()
        self.game_state = game_state
        self.manager = gui.UIManager()
        self.manager.enable()
        
        # Setup back button
        back_button = gui.UIFlatButton(text="Back to Game", width=200)
        back_button.on_click = self.on_back_click
        self.manager.add(
            gui.UIAnchorWidget(
                anchor_x="center",
                anchor_y="bottom",
                child=back_button,
                align_y=20
            )
        )
    
    def on_draw(self):
        arcade.start_render()
        
        # Title
        arcade.draw_text("Game Statistics", 
                        self.window.width // 2, 
                        self.window.height - 50,
                        arcade.color.BLACK, 30, anchor_x="center")
        
        # Column 1: Basic Stats
        stats_left = [
            f"Total Rounds: {self.game_state.cards_played // 2}",
            f"Player Wins: {self.game_state.player_wins}",
            f"Enemy Wins: {self.game_state.enemy_wins}",
            f"Ties: {self.game_state.ties}",
            f"Current Win Streak: {self.game_state.win_streak}",
            f"Longest Win Streak: {self.game_state.longest_win_streak}",
        ]
        
        for i, stat in enumerate(stats_left):
            arcade.draw_text(stat, 100, self.window.height - 120 - i*40, 
                           arcade.color.BLACK, 20)
        
        # Column 2: Deck Info
        stats_right = [
            f"Player Cards: {len(self.game_state.player_deck)}",
            f"Enemy Cards: {len(self.game_state.enemy_deck)}",
            f"Current War: {self.game_state.current_war}",
            f"Current Skirmish: {self.game_state.current_skirmish}",
            f"Current Hand: {self.game_state.current_hand}",
            f"Player Advantage: {self.game_state.player_advantage}",
            f"Score to Beat: {self.game_state.score_to_beat}",
        ]
        
        for i, stat in enumerate(stats_right):
            arcade.draw_text(stat, self.window.width // 2 + 100, 
                           self.window.height - 120 - i*40, 
                           arcade.color.BLACK, 20)
        
        self.manager.draw()
    
    def on_back_click(self, event):
        self.window.show_view(self.previous_view)