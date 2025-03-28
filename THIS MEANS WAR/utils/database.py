# database.py
from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from typing import Optional, TypedDict, List, Dict, Any
from dataclasses import dataclass
import random
from constants import PROFILE_EMOJIS

# Type definitions
class SaveGameData(TypedDict):
    id: int
    profile_id: int
    player_deck: List[Dict[str, Any]]
    enemy_deck: List[Dict[str, Any]]
    player_score: int
    enemy_score: int
    total_rounds: int
    player_wins: int
    enemy_wins: int
    ties: int
    cards_played: int
    win_streak: int
    longest_win_streak: int
    played_cards: List[str]
    current_war: int
    current_skirmish: int
    current_hand: int
    player_advantage: int
    enemy_advantage: int

@dataclass
class Profile:
    id: int
    name: str
    emoji: str

@dataclass
class GameSave:
    id: int
    profile_id: int
    total_rounds: int
    player_score: int
    enemy_score: int

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.db_file = "game_saves.db"
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    emoji TEXT NOT NULL
                )
            """)
            conn.execute("""
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    action TEXT NOT NULL,
                    details TEXT
                )
            """)
            conn.commit()
    
    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_file)
    
    def create_profile(self, name: str) -> Profile:
        """Create a new profile with a random emoji"""
        emoji = random.choice(PROFILE_EMOJIS)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO profiles (name, emoji) VALUES (?, ?)",
                (name, emoji)
            )
            profile_id = cursor.lastrowid
            conn.commit()
        
        self._log_action("CREATE_PROFILE", {
            "profile_id": profile_id,
            "name": name,
            "emoji": emoji
        })
        return Profile(profile_id, name, emoji)
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile and all its saves"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name, emoji FROM profiles WHERE id = ?",
                (profile_id,)
            )
            if profile := cursor.fetchone():
                name, emoji = profile
                cursor.execute(
                    "DELETE FROM saves WHERE profile_id = ?",
                    (profile_id,)
                )
                cursor.execute(
                    "DELETE FROM profiles WHERE id = ?",
                    (profile_id,)
                )
                conn.commit()
                
                self._log_action("DELETE_PROFILE", {
                    "profile_id": profile_id,
                    "name": name,
                    "emoji": emoji
                })
                return True
        return False
    
    def list_profiles(self) -> List[Profile]:
        """List all available profiles"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, emoji FROM profiles")
            return [Profile(*row) for row in cursor.fetchall()]
    
    def save_game_state(self, profile_id: int, game_state: Dict[str, Any]) -> int:
        """
        Save the current game state
        Returns the save ID
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO saves (
                    profile_id, player_deck, enemy_deck, player_score, enemy_score,
                    total_rounds, player_wins, enemy_wins, ties, cards_played,
                    win_streak, longest_win_streak, played_cards, current_war,
                    current_skirmish, current_hand, player_advantage, enemy_advantage
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id,
                json.dumps(game_state["player_deck"]),
                json.dumps(game_state["enemy_deck"]),
                game_state["player_score"],
                game_state["enemy_score"],
                game_state["total_rounds"],
                game_state["player_wins"],
                game_state["enemy_wins"],
                game_state["ties"],
                game_state["cards_played"],
                game_state["win_streak"],
                game_state["longest_win_streak"],
                json.dumps(game_state["played_cards"]),
                game_state["current_war"],
                game_state["current_skirmish"],
                game_state["current_hand"],
                game_state["player_advantage"],
                game_state["enemy_advantage"]
            ))
            save_id = cursor.lastrowid
            conn.commit()
        
        self._log_action("SAVE_GAME", {
            "profile_id": profile_id,
            "save_id": save_id,
            **{k: game_state[k] for k in [
                "player_score", "enemy_score", "current_war",
                "current_skirmish", "current_hand",
                "player_advantage", "enemy_advantage"
            ]}
        })
        return save_id
    
    def load_game_state(self, profile_id: int, save_id: Optional[int] = None) -> Optional[SaveGameData]:
        """Load a game state, either specific save or most recent"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if save_id:
                cursor.execute(
                    "SELECT * FROM saves WHERE profile_id = ? AND id = ?",
                    (profile_id, save_id)
                )
            else:
                cursor.execute(
                    "SELECT * FROM saves WHERE profile_id = ? ORDER BY id DESC LIMIT 1",
                    (profile_id,)
                )
            
            if not (save_data := cursor.fetchone()):
                return None
            
            # Convert to typed dictionary
            return {
                "id": save_data[0],
                "profile_id": save_data[1],
                "player_deck": json.loads(save_data[2]),
                "enemy_deck": json.loads(save_data[3]),
                "player_score": save_data[4],
                "enemy_score": save_data[5],
                "total_rounds": save_data[6],
                "player_wins": save_data[7],
                "enemy_wins": save_data[8],
                "ties": save_data[9],
                "cards_played": save_data[10],
                "win_streak": save_data[11],
                "longest_win_streak": save_data[12],
                "played_cards": json.loads(save_data[13]),
                "current_war": save_data[14],
                "current_skirmish": save_data[15],
                "current_hand": save_data[16],
                "player_advantage": save_data[17],
                "enemy_advantage": save_data[18]
            }
    
    def list_saves(self, profile_id: int) -> List[GameSave]:
        """List all saves for a profile"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, profile_id, total_rounds, player_score, enemy_score "
                "FROM saves WHERE profile_id = ?",
                (profile_id,)
            )
            return [GameSave(*row) for row in cursor.fetchall()]
    
    def _log_action(self, action: str, details: Optional[Dict] = None):
        """Internal method for logging actions"""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO logs (action, details) VALUES (?, ?)",
                (action, json.dumps(details) if details else None)
            )
            conn.commit()
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent logs for debugging"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT timestamp, action, details FROM logs "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            return [
                {
                    "timestamp": row[0],
                    "action": row[1],
                    "details": json.loads(row[2]) if row[2] else None
                }
                for row in cursor.fetchall()
            ]

# Singleton instance
db = DatabaseManager()