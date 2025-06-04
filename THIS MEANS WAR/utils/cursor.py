# utils/ui.py

import time

class BlinkingCursor:
    def __init__(self, blink_rate: float = 0.5):
        self.blink_rate = blink_rate
        self.visible = True
        self.last_toggle_time = time.time()

    def update(self):
        current_time = time.time()
        if current_time - self.last_toggle_time > self.blink_rate:
            self.visible = not self.visible
            self.last_toggle_time = current_time
