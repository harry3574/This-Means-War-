import json
from pathlib import Path

SAVE_FILE = "game_save.json"

def save_game(player_deck, enemy_deck, player_score, enemy_score, total_rounds, player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards):
    """Save the current game state to a file."""
    game_state = {
        "player_deck": player_deck,
        "enemy_deck": enemy_deck,
        "player_score": player_score,
        "enemy_score": enemy_score,
        "total_rounds": total_rounds,
        "player_wins": player_wins,
        "enemy_wins": enemy_wins,
        "ties": ties,
        "cards_played": cards_played,
        "win_streak": win_streak,
        "longest_win_streak": longest_win_streak,
        "played_cards": played_cards,
    }

    with open(SAVE_FILE, "w") as file:
        json.dump(game_state, file, indent=4)

def load_game():
    """Load the game state from a file."""
    if not Path(SAVE_FILE).exists():
        return None  # No save file found

    with open(SAVE_FILE, "r") as file:
        game_state = json.load(file)

    return game_state

def view_save_file():
    """Read and return the contents of the save file."""
    if not Path(SAVE_FILE).exists():
        return "No save file found."

    with open(SAVE_FILE, "r") as file:
        return json.dumps(json.load(file), indent=4)