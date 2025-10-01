import random
import os

class Card:
    def __init__(self, color, value):
        self.color = color
        self.value = value
    
    def __str__(self):
        if self.color == "Wild":
            return f"{self.value}"
        return f"{self.color} {self.value}"
    
    def matches(self, other):
        return (self.color == other.color or 
                self.value == other.value or 
                self.color == "Wild" or 
                other.color == "Wild")

class Deck:
    def __init__(self):
        self.cards = []
        self.create_deck()
        self.shuffle()
    
    def create_deck(self):
        colors = ["Red", "Blue", "Green", "Yellow"]
        values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Skip", "Reverse", "Draw Two"]
        
        # Create colored cards
        for color in colors:
            # One zero per color
            self.cards.append(Card(color, "0"))
            # Two of each other card per color
            for value in values[1:]:
                self.cards.append(Card(color, value))
                self.cards.append(Card(color, value))
        
        # Create wild cards
        for _ in range(4):
            self.cards.append(Card("Wild", "Wild"))
            self.cards.append(Card("Wild", "Draw Four"))
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw_card(self):
        if len(self.cards) == 0:
            return None
        return self.cards.pop()
    
    def add_card(self, card):
        self.cards.append(card)

class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
    
    def draw_card(self, deck, count=1):
        for _ in range(count):
            card = deck.draw_card()
            if card:
                self.hand.append(card)
    
    def play_card(self, index, discard_pile):
        if 0 <= index < len(self.hand):
            card = self.hand.pop(index)
            discard_pile.append(card)
            return card
        return None
    
    def has_playable_card(self, top_card):
        return any(card.matches(top_card) for card in self.hand)
    
    def display_hand(self):
        print(f"\n{self.name}'s Hand:")
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}")
    
    def get_playable_cards(self, top_card):
        return [i for i, card in enumerate(self.hand) if card.matches(top_card)]

class UnoGame:
    def __init__(self, player_names):
        self.deck = Deck()
        self.players = [Player(name) for name in player_names]
        self.discard_pile = []
        self.current_player = 0
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise
        self.game_over = False
        
        # Deal initial cards
        for player in self.players:
            player.draw_card(self.deck, 7)
        
        # Start with first non-wild card
        while True:
            card = self.deck.draw_card()
            if card.color != "Wild":
                self.discard_pile.append(card)
                break
            else:
                self.deck.add_card(card)
                self.deck.shuffle()
    
    def next_player(self):
        self.current_player = (self.current_player + self.direction) % len(self.players)
    
    def handle_special_card(self, card):
        if card.value == "Skip":
            self.next_player()
            print(f"{self.players[self.current_player].name} was skipped!")
        elif card.value == "Reverse":
            self.direction *= -1
            print("Direction reversed!")
        elif card.value == "Draw Two":
            self.next_player()
            self.players[self.current_player].draw_card(self.deck, 2)
            print(f"{self.players[self.current_player].name} draws 2 cards!")
        elif card.value == "Draw Four":
            self.next_player()
            self.players[self.current_player].draw_card(self.deck, 4)
            print(f"{self.players[self.current_player].name} draws 4 cards!")
        elif card.value == "Wild":
            # Player already chose color during their turn
            pass
    
    def play_turn(self):
        current_player = self.players[self.current_player]
        top_card = self.discard_pile[-1]
        
        print(f"\n{'='*50}")
        print(f"Top card: {top_card}")
        current_player.display_hand()
        
        # Check if player has playable cards
        playable_indices = current_player.get_playable_cards(top_card)
        
        if not playable_indices:
            print("No playable cards! Drawing a card...")
            current_player.draw_card(self.deck)
            if current_player.has_playable_card(top_card):
                print("Drew a playable card!")
                playable_indices = current_player.get_playable_cards(top_card)
            else:
                print("Still no playable cards. Turn skipped.")
                self.next_player()
                return
        
        # Get player's move
        while True:
            try:
                choice = input("Choose a card to play (or 'd' to draw): ").lower()
                
                if choice == 'd':
                    current_player.draw_card(self.deck)
                    if current_player.has_playable_card(top_card):
                        print("Drew a playable card!")
                        playable_indices = current_player.get_playable_cards(top_card)
                        continue
                    else:
                        print("No playable card drawn. Turn skipped.")
                        self.next_player()
                        return
                else:
                    card_index = int(choice)
                    if card_index in playable_indices:
                        played_card = current_player.play_card(card_index, self.discard_pile)
                        break
                    else:
                        print("Invalid card! Choose a playable card.")
            except (ValueError, IndexError):
                print("Invalid input! Enter a valid card number or 'd' to draw.")
        
        # Handle wild card color choice
        if played_card.color == "Wild":
            while True:
                color_choice = input("Choose color (Red/Blue/Green/Yellow): ").capitalize()
                if color_choice in ["Red", "Blue", "Green", "Yellow"]:
                    played_card.color = color_choice
                    break
                else:
                    print("Invalid color choice!")
        
        # Check for UNO
        if len(current_player.hand) == 1:
            print(f"UNO! {current_player.name} has one card left!")
        
        # Check for win
        if len(current_player.hand) == 0:
            print(f"\n🎉 {current_player.name} wins! 🎉")
            self.game_over = True
            return
        
        # Handle special card effects
        self.handle_special_card(played_card)
        
        # Move to next player
        self.next_player()
    
    def play_game(self):
        print("Welcome to UNO!")
        print("Rules: Match cards by color or value. Special cards have special effects!")
        print("Enter 'd' to draw a card when it's your turn.\n")
        
        while not self.game_over:
            self.play_turn()

def main():
    print("UNO Card Game")
    
    # Get player names
    num_players = int(input("Enter number of players (2-4): "))
    player_names = []
    
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        player_names.append(name)
    
    # Start game
    game = UnoGame(player_names)
    game.play_game()

if __name__ == "__main__":
    main()