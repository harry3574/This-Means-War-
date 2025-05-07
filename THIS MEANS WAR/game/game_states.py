# /game/game_states.py
from enum import Enum, auto
from typing import List, Dict, Any
import json
from game.card import Card

class GameState:
    def to_dict(self) -> Dict[str, Any]:
        """Convert game state to serializable dictionary"""
        return vars(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create game state from dictionary"""
        state = cls()
        state.__dict__.update(data)
        return state

class Hand(GameState):
    def __init__(self):
        self.player_card: Card = None
        self.ai_card: Card = None
        self.player_pressure: int = 0
        self.ai_pressure: int = 0
        self.outcome: str = ""
        self.history_entry: str = ""
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        # Convert Card objects to dicts
        if self.player_card:
            data['player_card'] = {'suit': self.player_card.suit, 'value': self.player_card.value}
        if self.ai_card:
            data['ai_card'] = {'suit': self.ai_card.suit, 'value': self.ai_card.value}
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        hand = super().from_dict(data)
        # Convert dicts back to Cards
        if 'player_card' in data:
            hand.player_card = Card(data['player_card']['suit'], data['player_card']['value'])
        if 'ai_card' in data:
            hand.ai_card = Card(data['ai_card']['suit'], data['ai_card']['value'])
        return hand

class Skirmish(GameState):
    def __init__(self):
        self.hands: List[Hand] = []
        self.hands_played: int = 0
        self.player_skirmish_pressure: int = 0
        self.ai_skirmish_pressure: int = 0
        self.is_complete: bool = False
        self.battle_history: List[str] = []
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data['hands'] = [
            hand.to_dict() if hasattr(hand, 'to_dict') else hand
            for hand in self.hands
        ]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        skirmish = super().from_dict(data)
        # Convert list of dicts back to Hand objects
        skirmish.hands = [Hand.from_dict(hand_data) for hand_data in data.get('hands', [])]
        return skirmish

class War(GameState):
    def __init__(self):
        self.skirmishes: List[Skirmish] = []
        self.current_skirmish_index: int = 0
        self.player_war_pressure: int = 0
        self.ai_war_pressure: int = 0
        self.is_victory: bool = False
        self.cumulative_history: List[str] = []
        
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        # Convert list of Skirmish objects to list of dicts
        data['skirmishes'] = [skirmish.to_dict() for skirmish in self.skirmishes]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        war = super().from_dict(data)
        # Convert list of dicts back to Skirmish objects
        war.skirmishes = [Skirmish.from_dict(skirmish_data) for skirmish_data in data.get('skirmishes', [])]
        return war

class GamePhase(Enum):
    HAND = auto()
    SKIRMISH = auto()
    WAR = auto()
    CAMPAIGN = auto()