# views/stats_view.py
import arcade
from arcade import View
from collections import Counter

class StatsView(View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.stats_text = arcade.Text("", 50, 50, arcade.color.BLACK, 24, multiline=True, width=1180)
        
    def on_draw(self):
        arcade.start_render()
        
        # Title
        arcade.draw_text(
            "Game Statistics",
            self.window.width//2,
            self.window.height - 50,
            arcade.color.BLACK,
            36,
            anchor_x="center"
        )
        
        # Compile stats
        stats = [
            f"Total Rounds: {self.game_view.total_rounds}",
            f"Player Wins: {self.game_view.player_wins}",
            f"Enemy Wins: {self.game_view.enemy_wins}",
            f"Ties: {self.game_view.ties}",
            f"Cards Remaining (Player): {len(self.game_view.player_deck)}",
            f"Cards Remaining (Enemy): {len(self.game_view.enemy_deck)}",
            f"Cards Played: {self.game_view.cards_played}",
            f"Current Win Streak: {self.game_view.win_streak}",
            f"Longest Win Streak: {self.game_view.longest_win_streak}",
            f"Most Common Card: {self.most_common_card()}",
            f"Current War: {self.game_view.current_war}",
            f"Current Skirmish: {self.game_view.current_skirmish}",
            f"Current Hand: {self.game_view.current_hand}",
            f"Player Advantage: {self.game_view.player_advantage}",
            f"Enemy Advantage: {self.game_view.enemy_advantage}",
            f"Score to Beat: {self.game_view.score_to_beat}"
        ]
        
        self.stats_text.text = "\n".join(stats)
        self.stats_text.draw()
        
        # Back button
        arcade.draw_text(
            "Press 'S' to return to game",
            self.window.width//2,
            30,
            arcade.color.BLACK,
            24,
            anchor_x="center"
        )

    def most_common_card(self):
        """Calculate most common card from played cards"""
        if not self.game_view.played_cards:
            return "None"
        counter = Counter(self.game_view.played_cards)
        most_common = counter.most_common(1)
        return most_common[0][0] if most_common else "None"

    def on_key_press(self, key, modifiers):
        if key == arcade.key.S:
            self.window.show_view(self.game_view)