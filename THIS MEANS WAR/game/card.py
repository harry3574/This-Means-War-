# game/card.py (updated)
import arcade
from constants import RED, BLACK, WHITE, YELLOW, CYAN, PASTEL_YELLOW, PASTEL_CYAN, PASTEL_RED

class CardSprite(arcade.Sprite):
    def __init__(self, card_data, center_x, center_y, 
                 is_player=True, hovered=False, selected=False, enemy_hovered=False):
        super().__init__()
        self.card_data = card_data
        self.is_player = is_player
        self.hovered = hovered
        self.selected = selected
        self.enemy_hovered = enemy_hovered
        self.scale = 0.5
        self.center_x = center_x
        self.center_y = center_y
        self.update_texture()
    
    def update_texture(self):
        """Generate texture based on card state"""
        # Create texture
        texture = arcade.Texture.create_empty(f"card_{id(self)}", (200, 300))
        
        # Draw background based on state
        if self.hovered:
            arcade.draw_rectangle_filled(100, 150, 200, 300, PASTEL_YELLOW)
        elif self.selected:
            arcade.draw_rectangle_filled(100, 150, 200, 300, PASTEL_CYAN)
        elif self.enemy_hovered:
            arcade.draw_rectangle_filled(100, 150, 200, 300, PASTEL_RED)
        else:
            arcade.draw_rectangle_filled(100, 150, 200, 300, WHITE)
        
        # Draw border
        arcade.draw_rectangle_outline(100, 150, 200, 300, BLACK, 2)
        
        # Set rank/suit color
        color = RED if self.card_data['suit'] in ['♥', '♦'] else BLACK
        
        # Draw rank and suit
        arcade.draw_text(
            self.card_data['rank'], 20, 250, 
            color, 24, 
            font_name="resources/fonts/unifont.ttf"
        )
        arcade.draw_text(
            self.card_data['suit'], 20, 220, 
            color, 24, 
            font_name="resources/fonts/unifont.ttf"
        )
        
        # Draw player/enemy label if needed
        if not (self.hovered or self.selected or self.enemy_hovered):
            label = "Player" if self.is_player else "Enemy"
            arcade.draw_text(
                label, 20, 30, 
                BLACK, 18,
                font_name="resources/fonts/unifont.ttf"
            )
        
        self.texture = texture