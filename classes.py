import random
from ascii_renderer import display_cards as PRINT_CARDS

class BlackJack:
    def __init__(self):
        # Ruleset:
        self.hole_card = True
        self.shoe_size = 2

        self.deck = Deck(self.shoe_size)

        self.player = Player()

        self.dealer = Dealer(hole_card=self.hole_card)

    def run_game(self):
        self.start_round()
        return

    def start_round(self):
        self.deck.shuffle()
        starting_cards = 2
        check_bet = False
        while not check_bet:
            while True:
                try:
                    _prompt_bet = int(input("Place your wager, mortal!\n"))
                    break
                except ValueError:
                    print("We'll stick to non-exotic denominations of currency for your sake, mortal!\nState your wager as a whole number!\n")

            check_bet = self.player.bet(_prompt_bet)
        print(f"ok.\nplayer funds:{self.player.funds}") #just for debugging
        for _ in range(starting_cards): # denne håndterer ikke hvis vi ikke har hole card.
            self.player.hand.add_card(self.deck.draw())
            self.dealer.add_card(self.deck.draw())

        #print(self.player.hand.cards)

        dealer_cards = self.dealer.hand
        player_cards = self.player.hand.cards
        #print(dealer_cards)
        #print(player_cards)
        PRINT_CARDS(dealer_cards)
        PRINT_CARDS(player_cards)

        print(f"Score is {self.player.hand.get_score()}")
        if self.player.hand.is_blackjack():
            self.dealer.show_hole_card()
            PRINT_CARDS(dealer_cards)
            PRINT_CARDS(player_cards)
            print("Blackjack wins!")






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
                "is_cursed": False,
                "face_down": False,
                "value_modifier": 0
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
        return (None)

    def __len__(self):
        return (len(self.deck))

    #can remove and use RenderDeck instead -Done
    # Valgte å flytte renderingslogikken ut til ascii_renderer
    # hadde den først som en egen klasse, men så det ble krøllete,
    # så konverterte til en fri funksjon, flyttet så denne ut for å holde
    # denne fila kun til klasser!
    # latt stå så du kan se hvor det starta x)
    r"""
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
        return (rendered_deck)
    """



#    def view_deck(self):
#        return self.deck

class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.funds = 10000 #D$
        self.bloodpool = 400 #cL

        self.hand = Hand()

    def bet(self, amount):
        if self.funds >= amount:
            self.funds -= amount
            self.hand.bet += amount
            print(f"{self.name} bet {amount}.")
            return (True)
        else:
            print(f"You don't have the funds for such a grand gamble!")
            return (False)


class Dealer:
    def __init__(self, hole_card=True):
        self.bank = 100000
        self.hole_card = hole_card

        self.hand = []
        # Valgte å håndtere dealers hånd internt i klassen, for å lettere kunne håndtere hole-card
        # hvis jeg kommer på en bedre måte å håndtere det på kan jeg dytte dealers funksjoner tilbake i Hand. en is_dealer sjekk kanskje?


    def show_hole_card(self):
        self.hand[1]["face_down"] = False

    def add_card(self, card):
        #print(card)
        if len(self.hand) == 1:
            #print(card["face_down"])
            card["face_down"] = True
            self.hand.append(card)
        else:
            self.hand.append(card)


class Hand:
    def __init__(self):
        self.cards = []
        self.bet = 0
        self.max_blackjack_cards = 2 #I've set it up like this so I can change it with powerups
        #self.is_done = False
        #self.is_doubled = False
        #self.turn = -2 hadde en idé som krevde at jeg tracka tur, men gikk bort fra det

    # glemte at jeg kunne gå på attributten direkte
    #def change_bet(self, bet):
    #    self.bet += bet

    def get_score(self):
        base_score = sum(card["value"] for card in self.cards)
        score_modifier = sum(card["value_modifier"] for card in self.cards)
        return (base_score + score_modifier)

    def add_card(self, card): # Expects a single card-dict
        self.cards.append(card)
        #self.turn += 1

    def is_splittable(self):
        if len(self.cards) == 2: #this might need tweeking, if i add cheats that alter this
            return (self.cards[0][1] == self.cards[1][1])
        return (False)

    def is_blackjack(self):
        if len(self.cards) == self.max_blackjack_cards:
            return (self.get_score == 21) # Returns True or False
        else:
            return (False)


deck = Deck(2)
deck.shuffle()

print("You are dealt:")
cards_to_deal = 2
dealt_cards =  []
for _ in range(cards_to_deal):
    dealt_cards.append(deck.draw())
PRINT_CARDS(dealt_cards)
#print(len(deck))

"""
for card in deck.list_rendered_deck():
    for line in card:
        print(line)
    print()
"""

game = BlackJack()
#game.deck.list_rendered_deck
game.run_game()




r"""
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
        face_down = (
            f"+===========+",
            f"|| + + + + ||",
            f"||+ + + + +||",
            f"|| + + + + ||",
            f"||+ + + + +||",
            f"|| + + + + ||",
            f"+===========+"
        )
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
            rendered_list.append(card_template if not card["face_down"] else face_down)

        self.rendered_cards = tuple(rendered_list)

    def display(self):
        if not self.rendered_cards:
            return
        for line_group in zip(*self.rendered_cards):
            print(" ".join(line_group))
"""