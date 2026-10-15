import random

class BlackJack:
    def __init__(self):
        # Ruleset:
        self.hole_card = True
        self.shoe_size = 2

        self.deck = Deck(self.shoe_size)

        self.player = Player()

        self.dealer = Dealer()

    def run_game(self):

        return

class Deck:
    SUITS = ["Hearts", "Clubs", "Spades", "Diamonds"]
    RANKS = [("2", 2), ("3", 3), ("4", 4), ("5", 5),
             ("6", 6), ("7", 7), ("8", 8), ("9", 9),
             ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
             ("A", 11)]

    def __init__(self, num_decks=1):
        #Generates the "shoe" (collection of decks)
        self.deck = [
            {
                "suit": suit,
                "rank": rank[0],
                "value": rank[1],
                "is_marked": False,
                "is_cursed": False
            }
            for _ in range(num_decks)
            for suit in self.SUITS
            for rank in self.RANKS
        ]

    def shuffle(self): #shuffles the deck in place
        random.shuffle(self.deck)

    def draw(self):
        if self.deck:
            drawn_card = self.deck.pop()
            return drawn_card
        return None

    def __len__(self):
        return len(self.deck)

    def list_rendered_deck(self):
        RED = "\033[91m"
        RESET = "\033[0m"

        SUIT_SYMBOLS = {
            "Hearts": f"{RED}♥{RESET}",
            "Diamonds": f"{RED}♦{RESET}",
            "Spades": "♠",
            "Clubs": "♣"
        }

        rendered_deck = []
        for card in self.deck:
            #rendered_card = []

            rank = card["rank"]
            suit = card["suit"]
            symbol = SUIT_SYMBOLS.get(suit, suit)
            card_template = [
                f"+-----------+",
                f"| {rank:<2}        |",
                f"|           |",
                f"|     {symbol}     |",
                f"|           |",
                f"|        {rank:>2} |",
                f"+-----------+"
            ]
            rendered_deck.append((line for line in card_template))
        return rendered_deck



#    def view_deck(self):
#        return self.deck

class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.dollaridoos = 10000 #D$
        self.bloodpool = 400 #cL

    def bet(self, amount):
        if self.dollaridoos >= amount:
            self.dollaridoos -= amount
            return f"{self.name} bet {amount}."
        else:
            return f"You don't have the funds for such a grand gamble!"





class Hand:
    def __init__(self, bet=0):
        self.cards = []
        self.bet = bet
        self.is_done = False
        self.is_doubled = False
        #self.turn = -2

    def add_card(self, card): # Expects a single card-dict
        self.cards.append(card)
        #self.turn += 1

    def is_splittable(self):
        if len(self.cards) == 2: #this might need tweeking, if i add cheats that alter this
            return self.cards[0][1] == self.cards[1][1]
        return False








#class Dealer:

# takes list of dicts and returns list of tuples
#convert to function
class RenderCard:
    RED = "\033[91m"
    RESET = "\033[0m"

    SUIT_SYMBOLS = {
        "Hearts": f"{RED}♥{RESET}",
        "Diamonds": f"{RED}♦{RESET}",
        "Spades": "♠",
        "Clubs": "♣"
    }
    def __init__(self, cards):
        rendered_list = []
        for card in cards:
            suit = card["suit"]
            rank = card["rank"]
            symbol = self.SUIT_SYMBOLS.get(suit, suit)
            card_template = (
                f"+-----------+",
                f"| {rank:<2}        |",
                f"|           |",
                f"|     {symbol}     |",
                f"|           |",
                f"|        {rank:>2} |",
                f"+-----------+"
            )
            rendered_list.append(card_template)

        self.rendered_cards = tuple(rendered_list)

    def display(self):
        if not self.rendered_cards:
            return
        for line_group in zip(*self.rendered_cards):
            print(" ".join(line_group))



deck = Deck(2)

deck.shuffle()



print("You are dealt:")

cards_to_deal = 2

dealt_cards =  []
for _ in range(cards_to_deal):
    dealt_cards.append(deck.draw())

RenderCard(dealt_cards).display()



#print(len(deck))

"""
for card in deck.list_rendered_deck():
    for line in card:
        print(line)
    print()
"""