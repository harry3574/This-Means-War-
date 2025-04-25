from enum import Enum, auto
from typing import List
from game.card import Card

class GameState:
    pass

class Hand(GameState):
    def __init__(self):
        self.player_card: Card = None
        self.ai_card: Card = None
        self.player_pressure: int = 0
        self.ai_pressure: int = 0
        self.outcome: str = ""  # "win", "loss", "war"
        self.history_entry: str = ""

class Skirmish(GameState):
    def __init__(self):
        self.hands: List[Hand] = []
        self.hands_played: int = 0
        self.player_skirmish_pressure: int = 0
        self.ai_skirmish_pressure: int = 0
        self.is_complete: bool = False
        self.battle_history: List[str] = []

class War(GameState):
    def __init__(self):
        self.skirmishes: List[Skirmish] = []
        self.current_skirmish_index: int = 0
        self.player_war_pressure: int = 0
        self.ai_war_pressure: int = 0
        self.is_victory: bool = False
        self.cumulative_history: List[str] = []

class GamePhase(Enum):
    HAND = auto()
    SKIRMISH = auto()
    WAR = auto()
    CAMPAIGN = auto()