from typing import List
from game.card import Card
import random

class WarGame:
    def __init__(self):
        self.player_hand: List[Card] = []
        self.ai_hand: List[Card] = []
        self.deck: List[Card] = []
        self.battle_history: List[str] = []
        self.initialize_game()
        
    def initialize_game(self):
        """Create a 48-card deck (no jokers) and deal cards"""
        suits = ['♠', '♥', '♦', '♣']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        # Create deck with 48 cards (remove some cards to make it 48)
        self.deck = [Card(suit, value) for suit in suits for value in values][:48]
        random.shuffle(self.deck)
        
        # Deal 24 cards to each player
        self.player_hand = self.deck[:24]
        self.ai_hand = self.deck[24:]
        
    def swap_player_cards(self, index1: int, index2: int):
        """Swap two cards in player's hand"""
        if 0 <= index1 < len(self.player_hand) and 0 <= index2 < len(self.player_hand):
            self.player_hand[index1], self.player_hand[index2] = (
                self.player_hand[index2], self.player_hand[index1]
            )
    
    def resolve_battle(self):
        """Resolve the current battle according to war rules"""
        if not self.player_hand or not self.ai_hand:
            return
            
        player_card = self.player_hand.pop(0)
        ai_card = self.ai_hand.pop(0)
        
        if player_card.rank > ai_card.rank:
            # Player wins
            self.player_hand.extend([player_card, ai_card])
            self.battle_history.append(f"You won: {player_card} beats {ai_card}")
        elif ai_card.rank > player_card.rank:
            # AI wins
            self.ai_hand.extend([ai_card, player_card])
            self.battle_history.append(f"You lost: {ai_card} beats {player_card}")
        else:
            # War!
            self.battle_history.append(f"War! {player_card} ties {ai_card}")
            self.resolve_war([player_card], [ai_card])
            
    def resolve_war(self, player_cards: List[Card], ai_cards: List[Card]):
        """Resolve a war situation"""
        # Check if players have enough cards for war
        if len(self.player_hand) < 3 or len(self.ai_hand) < 3:
            # Not enough cards - split remaining cards
            self.player_hand.extend(player_cards)
            self.ai_hand.extend(ai_cards)
            self.battle_history.append("Not enough cards for war - splitting remaining")
            return
            
        # Add face-down cards
        player_face_down = [self.player_hand.pop(0) for _ in range(2)]
        ai_face_down = [self.ai_hand.pop(0) for _ in range(2)]
        
        # Add face-up cards
        player_face_up = self.player_hand.pop(0)
        ai_face_up = self.ai_hand.pop(0)
        
        if player_face_up.rank > ai_face_up.rank:
            # Player wins war
            won_cards = player_cards + ai_cards + player_face_down + ai_face_down + [player_face_up, ai_face_up]
            self.player_hand.extend(won_cards)
            self.battle_history.append(f"You won the war: {player_face_up} beats {ai_face_up}")
        elif ai_face_up.rank > player_face_up.rank:
            # AI wins war
            won_cards = ai_cards + player_cards + ai_face_down + player_face_down + [ai_face_up, player_face_up]
            self.ai_hand.extend(won_cards)
            self.battle_history.append(f"You lost the war: {ai_face_up} beats {player_face_up}")
        else:
            # Another war!
            self.battle_history.append(f"Another war! {player_face_up} ties {ai_face_up}")
            self.resolve_war(
                player_cards + player_face_down + [player_face_up],
                ai_cards + ai_face_down + [ai_face_up]
            )
    
    def is_game_over(self) -> bool:
        """Check if game has ended"""
        return len(self.player_hand) == 0 or len(self.ai_hand) == 0
    
    def get_winner(self) -> str:
        """Determine the winner"""
        if len(self.player_hand) > len(self.ai_hand):
            return "player"
        elif len(self.ai_hand) > len(self.player_hand):
            return "ai"
        return "tie"