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
                player_advantage INTEGER,
                enemy_advantage INTEGER,
                FOREIGN KEY (profile_id) REFERENCES profiles (id)
            )
        """)
        conn.commit()

def create_profile(name):
    """Create a new profile with a name and a random emoji."""
    emoji = random.choice(PROFILE_EMOJIS)  # Assign a random emoji
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO profiles (name, emoji) VALUES (?, ?)", (name, emoji))
        conn.commit()

def delete_profile(profile_id):
    """Delete a profile and all associated saves."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saves WHERE profile_id = ?", (profile_id,))
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()

def list_profiles():
    """List all profiles with their emojis."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, emoji FROM profiles")
        return cursor.fetchall()

def save_game(profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds, player_wins, enemy_wins, ties, cards_played, win_streak, longest_win_streak, played_cards, current_war, current_skirmish, player_advantage, enemy_advantage):
    """Save the current game state to the database under a specific profile."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO saves (
                profile_id, player_deck, enemy_deck, player_score, enemy_score, total_rounds,
                player_wins, enemy_wins, ties, cards_played, win_streak,
                longest_win_streak, played_cards, current_war, current_skirmish,
                player_advantage, enemy_advantage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile_id, json.dumps(player_deck), json.dumps(enemy_deck), player_score, enemy_score, total_rounds,
            player_wins, enemy_wins, ties, cards_played, win_streak,
            longest_win_streak, json.dumps(played_cards), current_war, current_skirmish,
            player_advantage, enemy_advantage
        ))
        conn.commit()

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
        "player_advantage": save_data[16],
        "enemy_advantage": save_data[17]
    }

def list_saves(profile_id):
    """List all saved games for a specific profile."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, total_rounds, player_score, enemy_score FROM saves WHERE profile_id = ?", (profile_id,))
        return cursor.fetchall()
