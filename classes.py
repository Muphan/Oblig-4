import random
import ascii_renderer as ascii



class BlackJack:
    def __init__(self):
        # Ruleset:
        self.hole_card = True
        self.shoe_size = 2

        self.deck = Deck(self.shoe_size)
        self.players = []
        #self.player = Player()
        self.add_players_to_table()
        #self.players.append(self.player) # So i can expand to more players later

        self.dealer = Dealer(hole_card=self.hole_card)

    def add_players_to_table(self):
        print("Who shall join us for this round of wagers?")
        print("(Press ENTER on a blank line when all players are registered)\n")

        max_players = 5

        while len(self.players) < max_players:
            prompt = "State your name, Player 1!\n" if not self.players else f"Player {len(self.players) + 1} name (or press ENTER to start):\n"
            name = input(prompt).strip()

            # If user presses enter with nothing entered
            if not name:
                if len(self.players) >= 1:
                    break  # registration complete
                print("At least one player must join the table!")
                continue

            self.players.append(Player(name))

    def _prompt_player_bet(self, player):
        """Handles input, validation and subtracts bet from player's hand"""
        while True:
            try:
                amount = int(input(f"{player.name}, place your wager, mortal! (Funds: {player.funds})\n"))
                if amount <= 0:
                    print("You must wager a positive amount, mortal!\n")
                    continue

                # player.bet(amount) removes funds and returns True if player can afford the bet
                if player.bet(amount):
                    print(f"Wager accepted. Remaining funds: {player.funds}\n")
                    break
            except ValueError:
                print("State your wager as a whole number!\n")

    def check_initial_blackjacks(self):
        # Checks if dealer has blackjack
        dealer_is_jacked = self.dealer.hand.is_blackjack()

        if dealer_is_jacked:
            self.dealer.show_hole_card()
            ascii.display_table(self.dealer, self.players)
            print(f"But fortune does not shine upon you today, as I have blackjack!")

            # Sets Hand.is_done to True (Round over)
            for player in self.players:
                player.hands[0].is_done = True

                if player.hands[0].is_blackjack():
                    # "Push": Player gets bet back.
                    player.funds += player.hands[0].bet
                    print(f"But you shall have your coins back, {player.name}!")
                else:
                    # Loss: Dealer takes the funds
                    self.dealer.bank += player.hands[0].bet
                    print(f"Your wager is mine, {player.name}!")

            # Round is over for everyone
            return (True)

        for player in self.players:
            if player.hands[0].is_blackjack():
                payout = int(player.hands[0].bet * 2.5)
                player.funds += payout
                self.dealer.bank -= (payout - player.hands[0].bet)

                print(f"Well done {player.name}, Blackjack! Paid out {payout} D$")
                player.hands[0].is_done = True

        # Round continues for everybody else
        return (False)


    def start_round(self):
        self.deck.shuffle()

        # Prompt for bets
        for player in self.players:
            self._prompt_player_bet(player)

        # Deals out 2 cards, it's split up to not have to have a method just to handle dealers 2nd card
        for player in self.players:
            player.hands[0].add_card(self.deck.draw())
        self.dealer.hand.add_card(self.deck.draw())
        for player in self.players:
            player.hands[0].add_card(self.deck.draw())
        self.dealer.hand.add_card(self.deck.draw(), face_down=True)

        #Draw table
        ascii.display_table(self.dealer, self.players)

        # Checks for blackjacks
        check_game_state = self.check_initial_blackjacks()

        # Round opening is done
        return (check_game_state)

    def play_player_turns(self):
        """Loops through players that aren't done and lets them make choices"""
        for player in self.players:
            i = 0
            while i < len(player.hands):
                hand = player.hands[i]

                if hand.is_done:
                    i += 1
                    continue # Skipps if player got blackjack.

                self._handle_hand_turn(player, hand, hand_index=i)
                i += 1

    def _handle_hand_turn(self, player, hand, hand_index=None):
        """Handles a single hand"""
        while not hand.is_done:
            ascii.display_table(self.dealer, self.players)

            hand_label = f" (Hand {hand_index + 1})" if len(player.hands) > 1 else ""
            print(f"--- {player.name.upper()}'S TURN{hand_label}")

            if hand.get_score() == 21:
                print(f"{player.name} got 21 and stands automatically!")
                hand.is_done = True
                break

            can_split = (
                len(hand.cards) == 2
                and hand.cards[0]["rank"] == hand.cards[1]["rank"]
                and player.funds >= hand.bet
            )

            options = ["[H]it", "[S]tand"]
            if can_split:
                options.append("s[P]lit")

            choice = input(f"Choose your action ({', '.join(options)}): ").strip().lower()

            if choice == "h":
                hand.add_card(self.deck.draw())
                print(f"{player.name} drew a card.")

                # Bust check:
                if hand.get_score() > 21:
                    ascii.display_table(self.dealer, self.players)
                    print(f"BUST! Your hand exceeds 21, {player.name}! You lost your wager!")
                    self.dealer.bank += hand.bet
                    hand.is_done = True

            elif choice == "s":
                print(f"{player.name} stands!")
                hand.is_done = True

            elif choice == "p" and can_split:
                self._execute_split(player, hand_index)

            else:
                print(f"INVALID! Chose a valid option, {player.name}!\n")

    def _execute_split(self, player, hand_index):
        current_hand = player.hands[hand_index]

        # Takes bet out of funds
        player.funds -= current_hand.bet

        # Generates new hand with the same bet
        new_hand = Hand()
        new_hand.bet = current_hand.bet

        # Moves one card from original hand
        split_card = current_hand.cards.pop()
        new_hand.add_card(split_card)

        # Draw new cards to both hands
        current_hand.add_card(self.deck.draw())
        new_hand.add_card(self.deck.draw())

        player.hands.insert(hand_index + 1, new_hand)
        print(f"{player.name} split their hand! I congratulate you on your daring play!")

    def run_game(self):
        opening = self.start_round()
        if not opening: # If start round returns False, the game continues
            self.play_player_turns()

        return

    def cleanup_round(self):
        if hasattr(self.dealer.hand, "cards"):
            self.deck.collect_cards(self.dealer.hand.cards)
            self.dealer.hand.cards.clear()

        for player in self.players:
            for hand in player.hands:
                self.deck.collect_cards(hand.cards)
            player.reset_for_new_round()










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

    def collect_cards(self, cards):
        """Collects a list of cards, resets facing and puts them back in deck"""
        for card in cards:
            card["face_down"] = False
            # If roguelike-mods needs resetting between rounds in the future, add them here
            self.deck.append(card)

    def __len__(self):
        return (len(self.deck))


class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.funds = 10000 #D$
        self.bloodpool = 400 #cL

        self.hands = [Hand()]

    def bet(self, amount):
        if self.funds >= amount:
            self.funds -= amount
            self.hands[0].bet += amount
            print(f"{self.name} bet {amount}.")
            return (True)
        else:
            print(f"You don't have the funds for such a grand gamble!")
            return (False)

    def reset_for_new_round(self):
        self.hands = [Hand()]


class Dealer:
    def __init__(self, hole_card=True):
        self.bank = 100000
        self.hole_card = hole_card
        self.hand = Hand()

    def show_hole_card(self):
        self.hand[1]["face_down"] = False

    def reset_for_new_round(self):
        self.hands = [Hand()]



class Hand:
    def __init__(self):
        self.cards = []
        self.bet = 0
        self.max_blackjack_cards = 2 #I've set it up like this so I can change it with powerups
        self.is_done = False
        self.is_doubled = False
        #self.turn = -2 hadde en idé som krevde at jeg tracka tur, men gikk bort fra det


    def get_score(self):
        visible_cards = [card for card in self.cards if not card.get("face_down", False)]

        base_score = sum(card["value"] for card in visible_cards)
        score_modifier = sum(card["value_modifier"] for card in visible_cards)
        return (base_score + score_modifier)

    def add_card(self, card, face_down=False): # Expects a single card-dict
        if card:
            card["face_down"] = face_down
            self.cards.append(card)

    def is_splittable(self):
        if len(self.cards) == 2: #this might need tweeking, if i add cheats that alter this
            return (self.cards[0][1] == self.cards[1][1])
        return (False)

    def is_blackjack(self):
        if len(self.cards) != self.max_blackjack_cards:
            return (False)
        return (self.get_score() == 21)  # Returns True or False



deck = Deck(2)
deck.shuffle()

print("You are dealt:")
cards_to_deal = 2
dealt_cards =  []
for _ in range(cards_to_deal):
    dealt_cards.append(deck.draw())
ascii.display_cards(dealt_cards)
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









    #This method was in Deck, just keeping it here in the deprecated pile for later review.
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