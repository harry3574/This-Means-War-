from typing import List
from game.card import Card
import random
from game.game_states import Hand, Skirmish, War, GamePhase

class WarGame:
    def __init__(self):
        self.deck: List[Card] = []
        self.player_hand: List[Card] = []
        self.ai_hand: List[Card] = []
        self.player_discard: List[Card] = []
        self.ai_discard: List[Card] = []
        
        self.current_war: War = None
        self.current_skirmish: Skirmish = None
        self.current_hand: Hand = None
        self.game_phase: GamePhase = GamePhase.HAND
        
        self.initialize_new_campaign()
    
    @property
    def player_pressure(self):
        """Current player pressure from active skirmish"""
        return self.current_skirmish.player_skirmish_pressure if self.current_skirmish else 0
    
    @property
    def ai_pressure(self):
        """Current AI pressure from active skirmish"""
        return self.current_skirmish.ai_skirmish_pressure if self.current_skirmish else 0

    @player_pressure.setter
    def player_pressure(self, value):
        """Set player pressure through current skirmish"""
        if self.current_skirmish:
            self.current_skirmish.player_skirmish_pressure = value

    @ai_pressure.setter
    def ai_pressure(self, value):
        """Set AI pressure through current skirmish"""
        if self.current_skirmish:
            self.current_skirmish.ai_skirmish_pressure = value
    
    # ... rest of the WarGame implementation remains the same ...
    
    def initialize_new_campaign(self):
        """Start a new campaign (series of wars)"""
        self.current_war = self._create_new_war()
        self.current_skirmish = self.current_war.skirmishes[0]
        self._reset_deck_and_hands()
    
    def _create_new_war(self) -> War:
        """Create a new war with 3 skirmishes"""
        war = War()
        for _ in range(3):
            war.skirmishes.append(Skirmish())
        return war
    
    def _reset_deck_and_hands(self):
        """Reset the deck and deal new hands"""
        suits = ['♠', '♥', '♦', '♣']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [Card(suit, value) for suit in suits for value in values][:48]
        random.shuffle(self.deck)
        self.player_hand = self.deck[:24]
        self.ai_hand = self.deck[24:]
        self.player_discard = []
        self.ai_discard = []
    
    def start_next_hand(self):
        """Prepare for the next hand in the current skirmish"""
        if len(self.player_hand) == 0 and len(self.player_discard) == 0:
            self._end_current_skirmish()
            return
        
        self.current_hand = Hand()
        self.game_phase = GamePhase.HAND
    
    def resolve_current_hand(self):
        """Resolve the current hand with pressure system"""
        if not self.player_hand or not self.ai_hand:
            self._reshuffle_discards()
            if not self.player_hand or not self.ai_hand:
                self._end_current_skirmish()
                return
        
        player_card = self.player_hand.pop(0)
        ai_card = self.ai_hand.pop(0)
        
        # Add to discard piles
        self.player_discard.append(player_card)
        self.ai_discard.append(ai_card)
        
        # Calculate pressure
        player_pressure, ai_pressure = self.calculate_pressure(player_card, ai_card)
        
        # Update hand outcome
        self.current_hand.player_card = player_card
        self.current_hand.ai_card = ai_card
        self.current_hand.player_pressure = player_pressure
        self.current_hand.ai_pressure = ai_pressure
        
        if player_card.rank > ai_card.rank:
            self.current_hand.outcome = "win"
            self.player_hand.extend([player_card, ai_card])
            history_msg = (f"You won: {player_card} beats {ai_card} "
                          f"(+{player_pressure} Pressure)")
        elif ai_card.rank > player_card.rank:
            self.current_hand.outcome = "loss"
            self.ai_hand.extend([ai_card, player_card])
            history_msg = (f"You lost: {ai_card} beats {player_card} "
                          f"(AI +{ai_pressure} Pressure)")
        else:
            self.current_hand.outcome = "war"
            history_msg = f"War! {player_card} ties {ai_card} (No Pressure)"
        
        self.current_hand.history_entry = history_msg
        self.current_skirmish.battle_history.append(history_msg)
        self.current_war.cumulative_history.append(history_msg)
        
        # Update pressure totals
        self.current_skirmish.player_skirmish_pressure += player_pressure
        self.current_skirmish.ai_skirmish_pressure += ai_pressure
        
        # Add to skirmish history
        self.current_skirmish.hands.append(self.current_hand)
        self.current_skirmish.hands_played += 1
        
        # Check skirmish completion
        if self.current_skirmish.hands_played >= 28:
            self._end_current_skirmish()
    
    def _reshuffle_discards(self):
        """Reshuffle discard piles into decks when empty"""
        if len(self.player_hand) == 0 and self.player_discard:
            random.shuffle(self.player_discard)
            self.player_hand = self.player_discard
            self.player_discard = []
        
        if len(self.ai_hand) == 0 and self.ai_discard:
            random.shuffle(self.ai_discard)
            self.ai_hand = self.ai_discard
            self.ai_discard = []
    
    def _end_current_skirmish(self):
        """Finalize the current skirmish"""
        self.current_skirmish.is_complete = True
        
        # Update war pressure totals
        self.current_war.player_war_pressure += self.current_skirmish.player_skirmish_pressure
        self.current_war.ai_war_pressure += self.current_skirmish.ai_skirmish_pressure
        
        # Move to next skirmish or end war
        self.current_war.current_skirmish_index += 1
        
        if self.current_war.current_skirmish_index >= len(self.current_war.skirmishes):
            self._end_current_war()
        else:
            self.current_skirmish = self.current_war.skirmishes[self.current_war.current_skirmish_index]
            self._reset_deck_and_hands()
            self.game_phase = GamePhase.SKIRMISH
    
    def _end_current_war(self):
        """Finalize the current war"""
        self.current_war.is_victory = (self.current_war.player_war_pressure > 
                                      self.current_war.ai_war_pressure)
        # Here you would typically:
        # - Save war results
        # - Offer upgrades/choices (for roguelike progression)
        # - Start a new war or end campaign
        self.game_phase = GamePhase.WAR
        
    
    # ... (keep existing calculate_pressure and suit advantage methods) ...
        
    def calculate_pressure(self, player_card: Card, ai_card: Card) -> tuple:
        """Calculate pressure points for both players with proper win/loss handling"""
        rank_diff = player_card.rank - ai_card.rank
        suit_advantage = player_card.get_suit_advantage(ai_card.suit)
        
        # Calculate base pressure based on who wins
        if rank_diff > 0:  # Player wins
            base_pressure = rank_diff * 10
            player_pressure = int(base_pressure * suit_advantage)
            ai_pressure = -player_pressure
            
            # Ensure minimum pressure for wins
            player_pressure = max(5, player_pressure)
            ai_pressure = -player_pressure
            
        elif rank_diff < 0:  # AI wins
            base_pressure = abs(rank_diff) * 10
            ai_pressure = int(base_pressure / suit_advantage)  # Inverse for loser
            player_pressure = -ai_pressure
            
            # Ensure minimum pressure for wins
            ai_pressure = max(5, ai_pressure)
            player_pressure = -ai_pressure
            
        else:  # Tie
            player_pressure = 0
            ai_pressure = 0
        
        return player_pressure, ai_pressure
    
    def resolve_single_battle(self, player_card: Card, ai_card: Card):
        """Resolve one battle with corrected pressure system"""
        # Calculate pressure (now properly handles win/loss)
        player_pressure, ai_pressure = self.calculate_pressure(player_card, ai_card)
        
        # Create hand record
        hand = Hand()
        hand.player_card = player_card
        hand.ai_card = ai_card
        hand.player_pressure = player_pressure
        hand.ai_pressure = ai_pressure
        
        # Add to discard piles
        self.player_discard.append(player_card)
        self.ai_discard.append(ai_card)
        
        if player_pressure > 0:  # Player won
            hand.outcome = "win"
            self.player_hand.extend([player_card, ai_card])
            hand.history_entry = (f"You won: {player_card} beats {ai_card} "
                                f"(+{player_pressure} Pressure)")
        elif ai_pressure > 0:  # AI won
            hand.outcome = "loss"
            self.ai_hand.extend([ai_card, player_card])
            hand.history_entry = (f"You lost: {ai_card} beats {player_card} "
                                f"(AI +{ai_pressure} Pressure)")
        else:  # Tie
            hand.outcome = "war"
            hand.history_entry = f"War! {player_card} ties {ai_card}"
        
        # Update game state
        self.current_skirmish.hands.append(hand)
        self.current_skirmish.hands_played += 1
        self.current_skirmish.player_skirmish_pressure += player_pressure
        self.current_skirmish.ai_skirmish_pressure += ai_pressure
        self.current_skirmish.battle_history.append(hand.history_entry)
        self.current_war.cumulative_history.append(hand.history_entry)
    
    def is_game_over(self) -> bool:
        """Check if game has ended"""
        return (len(self.player_hand) == 0 and len(self.player_discard) == 0) or \
               (len(self.ai_hand) == 0 and len(self.ai_discard) == 0)
    
    def get_winner(self) -> str:
        """Determine the winner based on pressure"""
        if self.player_pressure > self.ai_pressure:
            return "player"
        elif self.ai_pressure > self.player_pressure:
            return "ai"
        return "tie"