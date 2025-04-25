import sqlite3
from pathlib import Path
import json
from typing import Optional, Dict, List
from game.card import Card
from game.game_states import GamePhase
from game.war_game import WarGame
import logging

class GameSaver:
    def __init__(self, db_name: str = "war_game_saves.db"):
        self.db_path = Path(__file__).parent / db_name
        self._init_db()
        
    def _init_db(self):
        """Initialize database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_name TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    player_hand TEXT NOT NULL,
                    ai_hand TEXT NOT NULL,
                    player_discard TEXT NOT NULL,
                    ai_discard TEXT NOT NULL,
                    game_phase TEXT NOT NULL,
                    war_state TEXT NOT NULL,
                    skirmish_state TEXT NOT NULL,
                    hand_state TEXT NOT NULL
                )
            """)
            conn.commit()

    def _serialize_cards(self, cards: List[Card]) -> str:
        """Convert list of cards to JSON string"""
        return json.dumps([{"suit": card.suit, "value": card.value} for card in cards])

    def _deserialize_cards(self, json_str: str) -> List[Card]:
        """Convert JSON string back to Card objects"""
        cards_data = json.loads(json_str)
        return [Card(card["suit"], card["value"]) for card in cards_data]

    def _serialize_state(self, state) -> str:
        """Serialize game state objects to JSON"""
        return json.dumps(state.__dict__) if state else "{}"

    def _deserialize_state(self, json_str: str, state_class):
        """Deserialize JSON to game state objects"""
        data = json.loads(json_str) if json_str else {}
        state = state_class()
        state.__dict__.update(data)
        return state

    def save_game(self, game: WarGame, save_name: str) -> bool:
        """Save current game state"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO saves (
                        save_name, player_hand, ai_hand, player_discard, ai_discard,
                        game_phase, war_state, skirmish_state, hand_state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    save_name,
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
            return True
        except Exception as e:
            logging.error(f"Error saving game: {e}")
            return False

    def load_game(self, save_name: str) -> Optional[WarGame]:
        """Load game state by save name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT player_hand, ai_hand, player_discard, ai_discard,
                           game_phase, war_state, skirmish_state, hand_state
                    FROM saves WHERE save_name = ?
                """, (save_name,))
                result = cursor.fetchone()
                
                if not result:
                    return None
                    
                game = WarGame()
                game.player_hand = self._deserialize_cards(result[0])
                game.ai_hand = self._deserialize_cards(result[1])
                game.player_discard = self._deserialize_cards(result[2])
                game.ai_discard = self._deserialize_cards(result[3])
                game.game_phase = GamePhase[result[4]]
                game.current_war = self._deserialize_state(result[5], War)
                game.current_skirmish = self._deserialize_state(result[6], Skirmish)
                game.current_hand = self._deserialize_state(result[7], Hand)
                
                return game
        except Exception as e:
            logging.error(f"Error loading game: {e}")
            return None

    def list_saves(self) -> Dict[str, str]:
        """Get list of all saves with timestamps"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT save_name, timestamp FROM saves ORDER BY timestamp DESC")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def delete_save(self, save_name: str) -> bool:
        """Delete a save by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saves WHERE save_name = ?", (save_name,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error deleting save: {e}")
            return False