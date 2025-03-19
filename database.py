from asyncio import constants
import sqlite3
import json  # Import JSON for safer serialization
from pathlib import Path
from constants import PROFILE_EMOJIS
import random

DATABASE_FILE = "game_saves.db"

def initialize_database():
    """Initialize the database and create the necessary tables."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Create profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                emoji TEXT NOT NULL
            )
        """)
        # Create saves table with profile_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                player_deck TEXT,
                enemy_deck TEXT,
                player_score INTEGER,
                enemy_score INTEGER,
                total_rounds INTEGER,
                player_wins INTEGER,
                enemy_wins INTEGER,
                ties INTEGER,
                cards_played INTEGER,
                win_streak INTEGER,
                longest_win_streak INTEGER,
                played_cards TEXT,
                current_war INTEGER,
                current_skirmish INTEGER,
                current_hand INTEGER,
                player_advantage INTEGER,
                enemy_advantage INTEGER,
                FOREIGN KEY (profile_id) REFERENCES profiles (id)
            )
        """)
        # Create logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                action TEXT NOT NULL,
                details TEXT
            )
        """)
        conn.commit()

def create_profile(name):
    """Create a new profile with a name and a random emoji."""
    emoji = random.choice(PROFILE_EMOJIS)  # Assign a random emoji
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO profiles (name, emoji) VALUES (?, ?)", (name, emoji))
        profile_id = cursor.lastrowid  # Get the ID of the newly created profile
        conn.commit()
    # Log the action
    log_action("CREATE_PROFILE", {
        "profile_id": profile_id,
        "name": name,
        "emoji": emoji
    })

def delete_profile(profile_id):
    """Delete a profile and all associated saves."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Retrieve profile details before deletion
        cursor.execute("SELECT name, emoji FROM profiles WHERE id = ?", (profile_id,))
        profile = cursor.fetchone()
        if profile:
            name, emoji = profile
            # Delete associated saves
            cursor.execute("DELETE FROM saves WHERE profile_id = ?", (profile_id,))
            # Delete the profile
            cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            conn.commit()
            # Log the action
            log_action("DELETE_PROFILE", {
                "profile_id": profile_id,
                "name": name,
                "emoji": emoji
            })
def list_profiles():
    """List all profiles with their emojis."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, emoji FROM profiles")
        return cursor.fetchall()

def save_game(profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds, player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards, current_war, current_skirmish, current_hand, player_advantage, enemy_advantage):
    """Save the current game state to the database under a specific profile."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO saves (
                profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds,
                player_wins, enemy_wins, ties, cards_played, win_streak,
                longest_win_streak, played_cards, current_war, current_skirmish,
                current_hand, player_advantage, enemy_advantage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id, json.dumps(player_deck), json.dumps(enemy_deck), player_score, enemy_score, total_rounds,
            player_wins, enemy_wins, ties, cards_played, win_streak,
            longest_win_streak, json.dumps(played_cards), current_war, current_skirmish,
            current_hand, player_advantage, enemy_advantage
        ))
        save_id = cursor.lastrowid  # Get the ID of the newly created save
        conn.commit()
    # Log the action
    log_action("SAVE_GAME", {
        "profile_id": profile_id,
        "save_id": save_id,
        "player_score": player_score,
        "enemy_score": enemy_score,
        "current_war": current_war,
        "current_skirmish": current_skirmish,
        "current_hand": current_hand,
        "player_advantage": player_advantage,
        "enemy_advantage": enemy_advantage
    })

def load_game(profile_id, save_id=None):
    """Load a game state from the database for a specific profile."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        if save_id:
            cursor.execute("SELECT * FROM saves WHERE profile_id = ? AND id = ?", (profile_id, save_id))
        else:
            cursor.execute("SELECT * FROM saves WHERE profile_id = ? ORDER BY id DESC LIMIT 1", (profile_id,))
        save_data = cursor.fetchone()

    if not save_data:
        return None

    # Log the action
    log_action("LOAD_GAME", {
        "profile_id": profile_id,
        "save_id": save_data[0],
        "player_score": save_data[4],
        "enemy_score": save_data[5],
        "current_war": save_data[14],
        "current_skirmish": save_data[15],
        "current_hand": save_data[16],
        "player_advantage": save_data[17],
        "enemy_advantage": save_data[18]
    })

    # Convert the saved data back into the correct format
    return {
        "id": save_data[0],
        "profile_id": save_data[1],
        "player_deck": json.loads(save_data[2]),  # Convert JSON string back to list
        "enemy_deck": json.loads(save_data[3]),  # Convert JSON string back to list
        "player_score": save_data[4],
        "enemy_score": save_data[5],
        "total_rounds": save_data[6],
        "player_wins": save_data[7],
        "enemy_wins": save_data[8],
        "ties": save_data[9],
        "cards_played": save_data[10],
        "win_streak": save_data[11],
        "longest_win_streak": save_data[12],
        "played_cards": json.loads(save_data[13]),  # Convert JSON string back to list
        "current_war": save_data[14],
        "current_skirmish": save_data[15],
        "current_hand": save_data[16],
        "player_advantage": save_data[17],
        "enemy_advantage": save_data[18]
    }

def list_saves(profile_id):
    """List all saved games for a specific profile."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, total_rounds, player_score, enemy_score FROM saves WHERE profile_id = ?", (profile_id,))
        return cursor.fetchall()


def log_action(action, details=None):
    """Log an action to the logs table."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO logs (action, details) VALUES (?, ?)
        """, (action, json.dumps(details) if details else None))
        conn.commit()

def view_logs():
    """Retrieve and display all logs."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        logs = cursor.fetchall()

    for log in logs:
        timestamp, action, details = log[1], log[2], log[3]
        details_dict = json.loads(details) if details else {}
        print(f"{timestamp} - {action}:")
        for key, value in details_dict.items():
            print(f"  {key}: {value}")