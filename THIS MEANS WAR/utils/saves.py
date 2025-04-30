# /utils/saves.py
import sqlite3
from pathlib import Path
import json
from typing import Optional, Dict, List, Tuple
from game.card import Card
from game.game_states import GamePhase, War, Skirmish, Hand
from game.war_game import WarGame
import logging
import random
from datetime import datetime

# Import emojis from constants
try:
    from utils.constant import PROFILE_EMOJIS
except ImportError:
    # Fallback if constants.py doesn't exist
    PROFILE_EMOJIS = ["😀", "😎", "🤠", "🧙", "🦊", "🐉", "🧝", "👑", 
                     ":D", "UwU", ":^D", "^-^", "OwO", ">_<", "T_T"]

class GameSaver:
    def __init__(self, db_name: str = "war_game_saves.db"):
        self.db_path = Path(__file__).parent / db_name
        self.current_profile_id = None
        self._init_db()
        
    def _init_db(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    emoji TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_played DATETIME
                )
            """)
            
            # Saves table with foreign key to profiles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    save_name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    player_hand TEXT NOT NULL,
                    ai_hand TEXT NOT NULL,
                    player_discard TEXT NOT NULL,
                    ai_discard TEXT NOT NULL,
                    game_phase TEXT NOT NULL,
                    war_state TEXT NOT NULL,
                    skirmish_state TEXT NOT NULL,
                    hand_state TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE,
                    UNIQUE (profile_id, save_name)
                )
            """)
                        
            # NEW: Logging table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    profile_id INTEGER,
                    action_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE SET NULL
                )
            """)
            conn.commit()
    
    def log_action(self, action_type: str, details: str = "", profile_id: Optional[int] = None):
        """Log an action to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO game_logs 
                    (profile_id, action_type, details) 
                    VALUES (?, ?, ?)
                """, (profile_id or self.current_profile_id, action_type, details))
                conn.commit()
        except Exception as e:
            logging.error(f"Error logging action: {e}")

    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Retrieve recent logs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT l.*, p.name as profile_name
                FROM game_logs l
                LEFT JOIN profiles p ON l.profile_id = p.id
                ORDER BY l.timestamp DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
    
        # NEW: Enhanced delete methods
    def delete_save(self, save_id: int) -> bool:
        """Delete a save and log the action"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saves WHERE id = ?", (save_id,))
                conn.commit()
                self.log_action("DELETE_SAVE", f"Deleted save ID {save_id}")
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting save: {e}")
            return False

    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile and all its saves (cascade)"""
        try:
            profile_info = self.get_profile(profile_id)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
                conn.commit()
                self.log_action("DELETE_PROFILE", 
                              f"Deleted profile '{profile_info['name']}' with {cursor.rowcount} saves")
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting profile: {e}")
            return False

    def _serialize_cards(self, cards: List[Card]) -> str:
        """Convert list of cards to JSON string"""
        return json.dumps([{"suit": card.suit, "value": card.value} for card in cards])

    def _deserialize_cards(self, json_str: str) -> List[Card]:
        """Convert JSON string back to Card objects"""
        if not json_str or json_str == "[]":
            return []
        cards_data = json.loads(json_str)
        return [Card(card["suit"], card["value"]) for card in cards_data]

    def _serialize_state(self, state) -> str:
        """Serialize game state objects to JSON"""
        if not state:
            return "{}"
        return json.dumps(state.__dict__)

    def _deserialize_state(self, json_str: str, state_class):
        """Deserialize JSON to game state objects"""
        if not json_str or json_str == "{}":
            return None
        data = json.loads(json_str)
        state = state_class()
        state.__dict__.update(data)
        return state

    # ===== PROFILE MANAGEMENT =====
    def create_profile(self, name: str) -> Tuple[bool, str]:
        """Create a new profile with random emoji"""
        if not name.strip():
            return False, "Profile name cannot be empty"
            
        try:
            emoji = random.choice(PROFILE_EMOJIS)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO profiles (name, emoji) VALUES (?, ?)",
                    (name.strip(), emoji)
                )
                conn.commit()
                return True, f"Profile '{name}' {emoji} created!"
        except sqlite3.IntegrityError:
            return False, f"Profile '{name}' already exists"
        except Exception as e:
            logging.error(f"Error creating profile: {e}")
            return False, f"Error creating profile: {str(e)}"

    def list_profiles(self) -> List[Dict]:
        """Get all profiles with their save counts and last played time"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Access columns by name
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.id, 
                    p.name, 
                    p.emoji, 
                    p.created_at,
                    p.last_played,
                    COUNT(s.id) as save_count,
                    MAX(s.timestamp) as last_save
                FROM profiles p
                LEFT JOIN saves s ON p.id = s.profile_id
                GROUP BY p.id
                ORDER BY p.last_played DESC, p.created_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_profile(self, profile_id: int) -> Optional[Dict]:
        """Get a single profile by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM profiles WHERE id = ?
            """, (profile_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    def set_current_profile(self, profile_id: int) -> bool:
        """Set the active profile and update last_played timestamp"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE profiles 
                    SET last_played = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (profile_id,))
                conn.commit()
                self.current_profile_id = profile_id
                return True
        except Exception as e:
            logging.error(f"Error setting profile: {e}")
            return False

    # ===== SAVE MANAGEMENT =====
    def save_game(self, game: WarGame, save_name: str) -> Tuple[bool, str]:
        """Save current game state to current profile"""
        if not self.current_profile_id:
            return False, "No profile selected"
            
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO saves (
                        profile_id, save_name, player_hand, ai_hand,
                        player_discard, ai_discard, game_phase,
                        war_state, skirmish_state, hand_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.current_profile_id, 
                    save_name.strip(),
                    self._serialize_cards(game.player_hand),
                    self._serialize_cards(game.ai_hand),
                    self._serialize_cards(game.player_discard),
                    self._serialize_cards(game.ai_discard),
                    game.game_phase.name,
                    self._serialize_state(game.current_war),
                    self._serialize_state(game.current_skirmish),
                    self._serialize_state(game.current_hand)
                ))
                conn.commit()
                return True, f"Game saved as '{save_name}'"
        except Exception as e:
            logging.error(f"Error saving game: {e}")
            return False, f"Error saving: {str(e)}"

    def load_game(self, save_id: int) -> Optional[WarGame]:
        """Load game state by save ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM saves WHERE id = ?
                """, (save_id,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                    
                # Update profile last played time
                self.set_current_profile(result["profile_id"])
                
                game = WarGame()
                game.player_hand = self._deserialize_cards(result["player_hand"])
                game.ai_hand = self._deserialize_cards(result["ai_hand"])
                game.player_discard = self._deserialize_cards(result["player_discard"])
                game.ai_discard = self._deserialize_cards(result["ai_discard"])
                game.game_phase = GamePhase[result["game_phase"]]
                game.current_war = self._deserialize_state(result["war_state"], War)
                game.current_skirmish = self._deserialize_state(result["skirmish_state"], Skirmish)
                game.current_hand = self._deserialize_state(result["hand_state"], Hand)
                
                return game
        except Exception as e:
            logging.error(f"Error loading game: {e}")
            return None

    def list_saves(self, profile_id: Optional[int] = None) -> List[Dict]:
        """Get saves for current or specified profile"""
        target_id = profile_id or self.current_profile_id
        if not target_id:
            return []
            
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.id,
                    s.save_name,
                    s.timestamp,
                    p.name as profile_name,
                    p.emoji as profile_emoji,
                    json_array_length(s.player_hand) as player_cards,
                    json_array_length(s.ai_hand) as ai_cards
                FROM saves s
                JOIN profiles p ON s.profile_id = p.id
                WHERE s.profile_id = ?
                ORDER BY s.timestamp DESC
            """, (target_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_save_info(self, save_id: int) -> Optional[Dict]:
        """Get detailed information about a save"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.*,
                    p.name as profile_name,
                    p.emoji as profile_emoji
                FROM saves s
                JOIN profiles p ON s.profile_id = p.id
                WHERE s.id = ?
            """, (save_id,))
            result = cursor.fetchone()
            return dict(result) if result else None

    # ===== UTILITY METHODS =====
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            return False

    def reset_database(self) -> bool:
        """WARNING: Completely resets the database (for debugging)"""
        try:
            self.db_path.unlink(missing_ok=True)
            self._init_db()
            return True
        except Exception as e:
            logging.error(f"Error resetting database: {e}")
            return False