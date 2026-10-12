import random


class Deck:
    def __init__(self, num_decks=1):
        suits = ["Hearts", "Clubs", "Spades", "Diamonds"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        #Generates the "shoe" (collection of decks)
        self.cards = [(suit, rank) for suit in suits for rank in ranks] * num_decks

    def shuffle(self): #shuffles the deck in place
        random.shuffle(self.cards)

    def draw(self):
        if self.cards:
            return self.cards.pop()
        return None

    def draw_random(self):
        if self.cards:
            

    def __len__(self):
        return len(self.cards)

    def view_deck(self):
        return self.cards

class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.dollaridoos = 10000
        self.bloodpool = 400



class Hand:
    def __init__(self, bet=0):
        self.cards = []
        self.bet = bet
        self.is_done = False
        self.is_doubled = False

    def add_card(self, card):
        self.cards.append(card)

    def is_splittable(self):
        if len(self.cards) == 2: #this might need tweeking, if i add cheats that alter this
            return self.cards[0][1] == self.cards[1][1]
        return False





#noe eye-candy jeg fikk gemini til å sette sammen for meg så jeg har noe å se på mens jeg bygger og tester:
# ANSI-fargekoder
RED = "\033[91m"
RESET = "\033[0m"

# Oppslagstabell for symboler og farger
SUIT_SYMBOLS = {
    "Hearts": f"{RED}♥{RESET}",
    "Diamonds": f"{RED}♦{RESET}",
    "Spades": "♠",
    "Clubs": "♣"
}


def format_card(card):
    """
    Tar imot et kort-tuple som ('Hearts', 'Ace') eller ('Spades', '10')
    og returnerer en formattert streng med farge og symbol.
    """
    suit, value = card
    symbol = SUIT_SYMBOLS.get(suit, suit)
    return f"[{value} {symbol}]"

def format_cards(cards):
    return [format_card(card) for card in cards]

def print_equal_decks(decks):

    for første_Stokk, andre_stokk in zip(decks[0], decks[1]):

        print(f"{første_Stokk} - {andre_stokk}")


deck = Deck(6)
fresh_deck = format_cards(deck.view_deck())
deck.shuffle()
shuffled_deck = format_cards(deck.view_deck().copy())

print_equal_decks([fresh_deck, shuffled_deck])

print("You are dealt:")

cards_to_deal = 2
for _ in range(cards_to_deal):
    print(f"{deck.deal()}")

print(deck.__len__())

