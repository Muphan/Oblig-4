import os
import random
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import ascii_renderer as ascii_render
import datetime
from enum import Enum

SAVES_DIR = "saves"

# Helper class to track gamephase in the app
class GamePhase(str, Enum):
    BETTING = "BETTING"
    DEALING = "DEALING"
    PLAYER_TURN = "PLAYER_TURN"
    DEALER_TURN = "DEALER_TURN"
    EVALUATION = "EVALUATION"
    ROUND_OVER = "ROUND_OVER"

@dataclass
class Hand:
    """Creates a hand instance, this instance holds the cards, tracks state with is_done, for players it also holds the bet"""
    cards: list = field(default_factory=list)
    bet: int = 0
    max_blackjack_cards: int = 2
    is_done: bool = False
    is_doubled: bool = False
    has_blackjack: bool = False

    def get_score(self):
        """ Checks and returns the value of the hands visible cards.
            Adjusts score down if total goes over 21 and one or more cards are aces"""
        visible_cards = [card for card in self.cards if not card.get("face_down", False)]
        base_score = sum(card["value"] for card in visible_cards)
        score_modifier = sum(card["value_modifier"] for card in visible_cards)

        # uses constructor to sum Aces in (visible) hand.
        aces = sum(1 for card in visible_cards if card.get("rank") == "A")

        score = base_score + score_modifier

        # Loops as long as there are "unused" Aces and score is >21,
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1

        return (score)

    def add_card(self, card, face_down=False): # Expects a single card-dict
        """adds a card to the self.cards list. It can be fed any card, but usually called with card=self.deck.draw(),
           face_down is mainly used for handling dealers hole card"""
        if card:
            card["face_down"] = face_down
            self.cards.append(card)

    def is_splittable(self):
        """Checks if the hand is splittable"""
        if len(self.cards) == 2: #this will need tweaking if I add cheats that alter this
            return (self.cards[0]["rank"] == self.cards[1]["rank"])
        return (False)

    def is_blackjack(self):
        """Checks if the hand is blackjack (2 first cards has a value of 21). The first check is a bit redundant since
            this method isn't called other places than the start of the round, when there's only been given 2 cards,
            but have it here to future-proof for roguelike mechanics later on"""
        if len(self.cards) != self.max_blackjack_cards:
            return (False)
        self.has_blackjack = (self.get_score() == 21)
        # changed this so has_blackjack is stored as an attribute in Hand, instead of just returning
        # the boolean from the check, I set the attribute, then returns it. as I found I needed to check this
        # more than one place, I figured it was better to just save it to an attribute for different checks.
        return  self.has_blackjack

@dataclass # swapped to dataclasses to make the save load process more seamless
class Player:
    """Creates a player object, takes name as a parameter when constructing the object"""
    name: str = "Player"
    funds: int = 10000
    bloodpool: bool = False
    blood: int = 5000
    hands: List['Hand'] = field(default_factory=list)

    def __post_init__(self):
        if not self.hands:
            self.hands = [Hand()]

    def bet(self, amount):
        """Check that player have enough funds, subracts the bet from available funds if they don't
            prints a message and returns False if they do not have enough funds """
        # I should probably move the >0 check I do in prompt_player_bet here
        # I just have to rewrite a bit to make that check accept a tuple: (bool, str)
        # so I can send the error message with the check from here.
        if self.funds >= amount:
            self.funds -= amount
            self.hands[0].bet += amount
            print(f"{self.name} bet {amount}.")
            return (True)
        else:
            print(f"You don't have the funds for such a grand gamble!")
            return (False)

    def reset_for_new_round(self):
        """Clears hand"""
        self.hands = [Hand()]

    @classmethod
    def from_dict(cls, data: dict):
        """Converts saved dictionary data back into Hand-instances"""
        raw_hands = data.pop("hands", [])
        hands = [Hand(**h) for h in raw_hands]
        return cls(**data, hands=hands)

@dataclass
class Dealer:
    """Creates a dealer instance"""
    bank:       int             = 100000 #Default value of bank
    hole_card:  bool            = True   #Default True, hole card is on
    hand:       Hand            = field(default_factory=Hand)

    def show_hole_card(self):
        """As dealers second card is drawn face down, this method turns that card to face up"""
        if len(self.hand.cards) > 1:
            self.hand.cards[1]["face_down"] = False

    def reset_for_new_round(self):
        """Clears hand"""
        self.hand = Hand()

    @classmethod
    def from_dict(cls, data: dict):
        """Method to reconstruct a Dealer instance from save data"""
        raw_hand = data.pop("hand", {})
        hand = Hand(**raw_hand) if isinstance(raw_hand, dict) else Hand()
        return cls(bank=data.get("bank", 100000), hole_card=data.get("hole_card", True), hand=hand)

@dataclass
class Deck:
    """Class attributes defining the suits and ranks of playing cards"""
    num_decks:    int                       = 6
    deck:         List[Dict[str, Any]]      = field(default_factory=list)
    discards:     List[Dict[str, Any]]      = field(default_factory=list)
    # I dont use discards for anything yet,
    # but when discard pile rule is implemented the discarded cards are stored here.

    # Template for the card constructor
    SUITS = ["Hearts", "Clubs", "Spades", "Diamonds"]
    RANKS = [("2", 2), ("3", 3), ("4", 4), ("5", 5),
             ("6", 6), ("7", 7), ("8", 8), ("9", 9),
             ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
             ("A", 11)]


    def __post_init__(self):
        """Checks if a deck exists (from load_game()) before generating a deck"""
        if not self.deck and not self.discards:
            self.build_deck()
            self.shuffle()

    def build_deck(self):
        """Generates the "shoe" (collection of decks); generator runs: <for suit in SUITS for rank in RANKS>,
                    this creates one complete deck for each loop in range(num_decks), and populates the list <self.deck>.
                    Each card is a dictionary containing important information:
                    suit: str(card suit)
                    rank: str(card rank)
                    value: int(card value)
                    is_marked: bool
                    is_cursed: bool
                    face_down: bool
                    value_modifier: int
                    """
        # I could save on some processing power here by just generating a deck of 52,
        # then just multiply it on the number of decks.
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
            for _ in range(self.num_decks)
            for suit in self.SUITS
            for rank in self.RANKS
        ]

    def shuffle(self):
        """Shuffles the deck"""
        random.shuffle(self.deck)

    def draw(self):
        """Draws one card from the deck"""
        if self.deck:
            # I've gone a bit back and forth on whether I want to take first or last element,
            # it doesn't really matter, as I do not append cards back into the deck during a round.
            # I was doing first elem for a while, but then realized that I had the program shift all indices
            # for no purpose, so went back to just taking the last element from the deck.
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

class BlackJack:
    """Main instance, is owner of Player, Dealer and Deck
       Contains and handles the game logic.
       Game is started by calling BlackJack.run_game()"""
    def __init__(self):
        # Ruleset and settings:
        self.hole_card = True
        self.shoe_size = 2
        self.dealer_stand_threshold = 17 # The assignment says dealer stands on >17, but BJ rules says >=17
        self.hit_on_soft = False          # If dealer should hit on soft 17 i.e Ace + 6
        self.MAX_HANDS = 4                  # Potential max hands resulting from splits
        self.allow_double_after_split = True # If player is allowed to double on a split hand
        self.max_players = 5                  # Setting to limit amount of players
        self.blackjack_payout_multi = 2.5      # Payout multiplier for getting blackjack

        # State handling for save/load and turn handling
        self.game_phase = GamePhase.BETTING
        self.current_player_index = 0
        self.current_hand_index = 0

        # Create a deck:
        self.deck = Deck(self.shoe_size)

        # Create players
        self.players = []
        self.add_players_to_table()

        # Creates dealer
        self.dealer = Dealer(hole_card=self.hole_card)

    #added properties to track current player and hand to
    #save where in a turn the game is when saving.
    @property
    def current_player(self):
        if 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None

    @property
    def current_hand(self):
        player = self.current_player
        if player and 0 <= self.current_hand_index < len(player.hands):
            return player.hands[self.current_hand_index]
        return None

    def add_players_to_table(self):
        """Method to add players to table"""
        print("Who shall join us for this round of wagers?")
        print("(Press ENTER on a blank line when all players are registered)\n")

        while len(self.players) < self.max_players:
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
        """Checks if dealer or players have blackjack. Returns True if all players and/or dealer has blackjack
           False if at least one player and dealer doesn't have blackjack"""
        # Checks if dealer has blackjack
        dealer_is_jacked = self.dealer.hand.is_blackjack()

        if dealer_is_jacked:
            self.dealer.show_hole_card()
            ascii_render.display_table(self.dealer, self.players)
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
                payout = int(player.hands[0].bet * self.blackjack_payout_multi) # Default multiplier 2.5
                player.funds += payout
                self.dealer.bank -= (payout - player.hands[0].bet)

                print(f"Well done {player.name}, Blackjack! Paid out {payout} D$")
                player.hands[0].is_done = True

        # Round continues for everybody else
        return (False)


    def start_round(self):
        """Starts the round of the game, handles the initial dealing of cards and initiates the blackjack check"""
        self.game_phase = GamePhase.BETTING
        self.current_player_index = 0
        self.current_hand_index = 0

        self.deck.shuffle()

        # Prompt for bets
        for player in self.players:
            self._prompt_player_bet(player)

        self.game_phase = GamePhase.DEALING

        # Deals out 2 cards, it's split up to not have to have a method just to handle dealers 2nd card
        for player in self.players:
            player.hands[0].add_card(self.deck.draw())
        self.dealer.hand.add_card(self.deck.draw())
        for player in self.players:
            player.hands[0].add_card(self.deck.draw())
        self.dealer.hand.add_card(self.deck.draw(), face_down=True)

        # Checks for blackjacks
        check_game_state = self.check_initial_blackjacks()
        if not check_game_state:
            self.game_phase = GamePhase.PLAYER_TURN

        # Round opening is done
        return (check_game_state)

    def play_player_turns(self):
        """Loops through each player and their hands, that aren't done, and lets them make choices"""
        for player_idx, player in enumerate(self.players):
            self.current_player_index = player_idx
            hand_idx = 0
            # Loops through all the hands of a player
            while hand_idx < len(player.hands):
                self.current_hand_index = hand_idx
                hand = player.hands[hand_idx]
                if hand.is_done:
                    hand_idx += 1
                    continue
                # starts the hand handling
                self._handle_hand_turn(player, hand, hand_index=hand_idx)
                hand_idx += 1

    def _handle_hand_turn(self, player, hand, hand_index=None):
        """Handles a single hand, takes player instance, player.hand instance and index of the hand"""
        while not hand.is_done:
            #draws "game table" in terminal
            ascii_render.display_table(self.dealer, self.players)

            hand_label = f" (Hand {hand_index + 1})" if len(player.hands) > 1 else ""
            print(f"--- {player.name.upper()}'S TURN{hand_label}")

            #Auto stand on a 21
            if hand.get_score() == 21:
                print(f"{player.name} got 21 and stands automatically!")
                hand.is_done = True
                break

            """
            Checks if player hand qualifies for splitting returns True if:
            - Only have 2 cards
            - That those cards have the same value/rank
            - That the player have funds = initial bet.
            - Check amount of current hands, apparently casinos allow up to 3-4 hands
            TODO: implement exception for aces, as you're only allowed to split one ace pair, and are not allowed to hit 
                  on a split ace. You only get 1 card per split Ace.
            """
            # Defining when split is available
            can_split = (

                # checks that they only have a starting hand
                len(hand.cards) == 2
                # checks that the hand is a "pair"
                and hand.cards[0]["rank"] == hand.cards[1]["rank"]
                # check if player has enough funds
                and player.funds >= hand.bet
                # checks if they are bellow the max hand threshold
                and len(player.hands) < self.MAX_HANDS
            )

            # Defining when double down is available
            can_double = (
                # check if player has enough funds
                player.funds >= hand.bet
                # checks that they only have a starting hand
                and len(hand.cards) == 2
                # checks if they're allowed to double a split (default = True)
                and (self.allow_double_after_split or len(player.hands) < 2)
            )

            options = ["[H]it", "[S]tand"]
            # Add split option if conditions are met
            if can_split:
                options.append("s[P]lit")
            # Add double option if conditions are met
            if can_double:
                options.append("[D]ouble")

            # Prompt player to choose from available options
            choice = input(f"Choose your action ({', '.join(options)}): ").strip().lower()

            # if HIT
            if choice == "h":
                hand.add_card(self.deck.draw())
                print(f"{player.name} drew a card.")

                # Bust check:
                if hand.get_score() > 21:
                    ascii_render.display_table(self.dealer, self.players)
                    print(f"BUST! Your hand exceeds 21, {player.name}! You lost your wager!")
                    self.dealer.bank += hand.bet
                    hand.is_done = True

            # STAND
            elif choice == "s":
                print(f"{player.name} stands!")
                hand.is_done = True

            # DOUBLE
            elif choice == "d":
                player.funds -= hand.bet
                hand.bet += hand.bet
                hand.add_card(self.deck.draw())
                print(f"{player.name} doubled down!")
                hand.is_done = True
                break

            # SPLIT
            elif choice == "p" and can_split:
                self._execute_split(player, hand_index)

            # INVALID input
            else:
                print(f"INVALID! Chose a valid option, {player.name}!\n")

    def play_dealer_turn(self):
        """Dealer reveals hand and draws until minimum 17"""
        self.game_phase = GamePhase.DEALER_TURN
        # sets hole card to face up
        self.dealer.show_hole_card()
        # redraws table
        ascii_render.display_table(self.dealer, self.players)

        # Checks for remaining players in play.
        active_hands = [
            # constructs list of active hands
            # itterates through all players
            hand for player in self.players
            # then each player hand
            for hand in player.hands
            #and puts the hand in the list if the score of the hand <=21
            #and it doesn't have blackjack
            if hand.get_score() <= 21
            and not hand.has_blackjack
        ]

        if not active_hands: # Ends the round if there are no players
            print("All players have busted, the game is over!")
            return

        print("--- DEALERS TURN ---")

        while self.dealer.hand.get_score() < self.dealer_stand_threshold: # dealer_stand_threshold default: 17
            print(f"Dealer draws a card...")
            card = self.deck.draw()
            self.dealer.hand.add_card(card)
            # redraws table
            ascii_render.display_table(self.dealer, self.players)

        dealer_score = self.dealer.hand.get_score()

        if dealer_score > 21:
            print(f"DEALER BUST!")
        else:
            print(f"Dealer stands with {dealer_score} points!")

    def settle_bets(self):
        """Settles bets for all active players"""
        self.game_phase = GamePhase.EVALUATION
        dealer_score = self.dealer.hand.get_score()
        dealer_busted = dealer_score > 21 #Boolean

        print("\n" + "=" * 40)
        print("            FINAL TALLY            ")
        print("=" * 40)

        # Iterate over players
        for player in self.players:
            # Iterate over player hands (if they split)
            for i, hand in enumerate(player.hands):
                hand_label = f" (Hand {i + 1})" if len(player.hands) > 1 else ""

                # skip hands that already busted
                if hand.get_score() > 21:
                    continue

#               # Discovered that I paid out twice. Consider moving the immediate blackjack payout here.
                # Otherwisee I need to store or pass the payout sum for BJ to this method
                # Solved by giving Hand the attribute has_blackjack,
                # setting the bool with is_blackjack and returning has_blackjack for all the checks that pertains to.
                if hand.has_blackjack:
                    print(f"Well played, {player.name}{hand_label} won with blackjack!")
                    continue

                player_score = hand.get_score()

                # checks if dealer busted or player hand beats dealer.
                if dealer_busted or player_score > dealer_score:
                    payout = hand.bet * 2
                    player.funds += payout
                    self.dealer.bank -= hand.bet #dealer bank only relevant for imagined rogelike mode.
                    print(f"Congratulations! {player.name}{hand_label} beats dealer!\n({player_score} vs {dealer_score})\n{player.name} won a payout of {payout} D$!")

                # Check for push
                elif player_score == dealer_score:
                    player.funds += hand.bet
                    print(f"PUSH! {player.name}'s hand is equal to dealers!")

                # If none of the above, dealer has won.
                else:
                    self.dealer.bank += hand.bet
                    # I could follow up with hand.bet = 0, but the hand will be wiped after this anyway.
                    print(f"LOSS! Dealer beats {player.name}'s hand!")

            print("=" * 40 + "\n")


    def _execute_split(self, player, hand_index):
        """Helper function for to split the hand"""
        #  <s>Make an option/setting to control if player is allowed to resplit</s>
        #  (default rule implemented: allowed up to 4 total hands, set to 2 to disallow).
        #  Rules also state that split aces are not allowed to be played further, might
        #  implement a toggle or game mechanic to bypass that in the future.
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

        if split_card.get("rank") == "A":
            current_hand.is_done = True
            new_hand.is_done = True

        player.hands.insert(hand_index + 1, new_hand)
        print(f"{player.name} split their hand! I congratulate you on your daring play!")

    def run_game(self):
        """The main game loop.
           -Starts by checking if any players are broke, only relevant for 2nd to n-th round.
           -Ends game if all players are broke
           -Starts a new round, start_round() returns:
            True if all players or dealer have blackjack.
            False if there's players left to continue the round.
            -Then it runs player turns -> dealer turn -> settles bets -> cleans up
            -Players given choice to play another round or quit"""
        print("\n=== THE TABLE IS SET ===")

        while True:
            for player in self.players[:]:
                if player.funds <= 0:
                    print(f"\n {player.name} has run out of funds, and is cast down into the pits!")
                    self.players.remove(player)

            # Check if there are players remaining
            if not self.players:
                RED = "\033[91m"
                RESET = "\033[0m"
                print(f"{'No players left!':^40}\n\n{RED}{'THE':^40}\n\n{'HOUSE':^40}\n\n{'ALWAYS':^40}\n\n{'WINS':^40}{RESET}")
                break

            round_over = self.start_round()

            if not round_over:
                self.play_player_turns()
                self.play_dealer_turn()
                self.settle_bets()

            self.cleanup_round()

            print("\n" + "-" * 40)
            choice = input("Press [ENTER] to play another round, or [Q]uit to leave the table: ").strip().lower()

            # Quit:
            if choice == "q":
                print("\nYou gather your winnings and step away from the table. Until next time, mortal...")
                break

    def cleanup_round(self):
        """Collects cards from hands and puts them back into the deck.
           When a discard-pile is implemented, Deck will handle incoming cards based on the settings.
           The current code treats the deck and played cards like a casino with advanced shuffling machines"""
        if hasattr(self.dealer.hand, "cards"):
            self.deck.collect_cards(self.dealer.hand.cards)
            self.dealer.hand.cards.clear()

        for player in self.players:
            for hand in player.hands:
                self.deck.collect_cards(hand.cards)
            player.reset_for_new_round()

    def save_game(self, save_name: str):
        """Save the game to a json file in the saves/-folder"""
        if not os.path.exists(SAVES_DIR):
            os.makedirs(SAVES_DIR)

        # cleans up savegame name, checks each character in the string to see if it's an alphanumeric
        # or one of the allowed special characters
        clean_name = "".join(c for c in save_name if c.isalnum() or c in (" ", "_", "-")).strip()
        if not clean_name:
            clean_name = "quicksave"

        # constructs filepath by joining savegame-name with default filepath
        filepath = os.path.join(SAVES_DIR, f"{clean_name}.json")

        # .json template, adds metadata for preview in gui
        save_data = {
            "metadata": {
                "save_name": clean_name,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "player_name": self.players[0].name if self.players else "Player",
                "funds": self.players[0].funds if self.players else 0,
            },
            "players": [asdict(player) for player in self.players],
            "dealer": asdict(self.dealer),
            "deck": asdict(self.deck),
            "current_player_index": self.current_player_index,
            "current_hand_index": self.current_hand_index,
            "game_phase": self.game_phase.value if isinstance(self.game_phase, GamePhase) else self.game_phase
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=4)
            print(f"Game saved to {filepath}")
            return True, filepath
        except Exception as e:
            print(f"Error saving game: {e}")
            return False, str(e)


    def load_game(self, filepath: str):
        """Load gamestate from a json file"""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.players = [Player.from_dict(player) for player in data.get("players", [])]
            self.dealer = Dealer.from_dict(data.get("dealer", {}))
            self.deck = Deck(**data.get("deck", {}))
            self.current_player_index = data.get("current_player_index", 0)
            self.current_hand_index = data.get("current_hand_index", 0)

            raw_phase = data.get("game_phase", "BETTING")
            self.game_phase = GamePhase(raw_phase) if raw_phase in GamePhase.__members__ else GamePhase.BETTING

            print(f"Game loaded from {filepath}")
            return True

        except Exception as e:
            print(f"Error loading game: {e}")
            return False


    # method to fetch all save games for displaying in "load game"-screen
    @staticmethod
    def get_all_saves():
        if not os.path.exists(SAVES_DIR): # check if save game directory exists
            return []
        saves = []
        for filename in os.listdir(SAVES_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(SAVES_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        metadata = data.get("metadata", {})
                        metadata['filepath'] = filepath
                        metadata['filename'] = filename
                        saves.append(metadata)
                except Exception:
                    continue

        saves.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
        return saves








"""
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


"""
for card in deck.list_rendered_deck():
    for line in card:
        print(line)
    print()
"""

#game = BlackJack()
#game.deck.list_rendered_deck
#game.run_game()









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