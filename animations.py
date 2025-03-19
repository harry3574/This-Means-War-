# animations.py
import pygame

class CardFlipAnimation:
    def __init__(self, card, start_pos, end_pos, duration=500):
        self.card = card
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.is_flipped = False

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        progress = min(elapsed_time / self.duration, 1.0)

        # Interpolate position
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

        # Flip card halfway through the animation
        if progress >= 0.5 and not self.is_flipped:
            self.is_flipped = True

        return (x, y), self.is_flipped

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time >= self.duration

class TextAnimation:
    def __init__(self, text, start_pos, end_pos, duration=1000, scale_factor=1.5):
        self.text = text
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.scale_factor = scale_factor

    def update(self):
        elapsed_time = pygame.time.get_ticks() - self.start_time
        progress = min(elapsed_time / self.duration, 1.0)

        # Interpolate position
        x = self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress
        y = self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress

        # Scale text
        scale = 1 + (self.scale_factor - 1) * (1 - abs(progress - 0.5) * 2)

        return (x, y), scale

    def is_finished(self):
        return pygame.time.get_ticks() - self.start_time >= self.duration