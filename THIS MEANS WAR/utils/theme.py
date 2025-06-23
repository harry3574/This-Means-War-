# theme.py
from utils.constant import HIGH_CONTRAST, LOW_CONTRAST

# Default to high contrast mode
_current_theme = HIGH_CONTRAST

def set_theme(theme_name: str):
    global _current_theme
    if theme_name.lower() == "high":
        _current_theme = HIGH_CONTRAST
    elif theme_name.lower() == "low":
        _current_theme = LOW_CONTRAST
    else:
        raise ValueError(f"Unknown theme '{theme_name}'")

def get_color(name: str):
    try:
        return _current_theme[name]
    except KeyError:
        raise KeyError(f"Color key '{name}' not found in the current theme")
