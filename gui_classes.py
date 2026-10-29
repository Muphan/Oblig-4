import os
import random
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import datetime
from enum import Enum

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVES_DIR = os.path.join(SCRIPT_DIR, "saves")


class GamePhase(str, Enum):
    BETTING = "BETTING"
    DEALING = "DEALING"
    PLAYER_TURN = "PLAYER_TURN"
    DEALER_TURN = "DEALER_TURN"
    EVALUATION = "EVALUATION"
    ROUND_OVER = "ROUND_OVER"
    GAME_OVER = "GAME_OVER"


@dataclass
class Hand:
    """Oppretter en hånd-instans. Holder kortene, sporer is_done og har bet for spillere."""
    cards: list = field(default_factory=list)
    bet: int = 0
    max_blackjack_cards: int = 2
    is_done: bool = False
    is_doubled: bool = False
    has_blackjack: bool = False

    def get_score(self) -> int:
        """Sjekker og returnerer poengsummen for synlige kort.
        Justerer ned dersom summen går over 21 og hånden har Ess."""
        visible_cards = [card for card in self.cards if not card.get("face_down", False)]
        base_score = sum(card["value"] for card in visible_cards)
        score_modifier = sum(card["value_modifier"] for card in visible_cards)

        aces = sum(1 for card in visible_cards if card.get("rank") == "A")
        score = base_score + score_modifier

        while score > 21 and aces > 0:
            score -= 10
            aces -= 1

        return score

    def is_soft(self) -> bool:
        """Returnerer True dersom et Ess fremdeles teller som 11 uten å buste."""
        visible_cards = [card for card in self.cards if not card.get("face_down", False)]
        score = sum(card["value"] for card in visible_cards) + sum(card["value_modifier"] for card in visible_cards)
        aces = sum(1 for card in visible_cards if card.get("rank") == "A")

        while score > 21 and aces > 0:
            score -= 10
            aces -= 1

        return aces > 0

    def add_card(self, card: dict, face_down: bool = False):
        """Legger til et kort i hånden. face_down brukes for dealerens skjulte kort."""
        if card:
            card["face_down"] = face_down
            self.cards.append(card)

    def is_splittable(self) -> bool:
        """Sjekker om hånden har to kort av lik verdi/rangering."""
        if len(self.cards) == 2:
            return self.cards[0]["rank"] == self.cards[1]["rank"]
        return False

    def is_blackjack(self) -> bool:
        """Sjekker om de to første kortene gir 21."""
        if len(self.cards) != self.max_blackjack_cards:
            return False
        self.has_blackjack = (self.get_score() == 21)
        return self.has_blackjack


@dataclass
class Player:
    """Oppretter en spiller-instans."""
    name: str = "Player 1"
    funds: int = 10000
    bloodpool: bool = False
    blood: int = 5000
    hands: List[Hand] = field(default_factory=list)

    def __post_init__(self):
        if not self.hands:
            self.hands = [Hand()]

    def bet(self, amount: int) -> bool:
        """Trekker fra saldo dersom spilleren har nok midler."""
        if self.funds >= amount and amount > 0:
            self.funds -= amount
            self.hands[0].bet += amount
            return True
        return False

    def reset_for_new_round(self):
        """Nullstiller hender for en ny runde."""
        self.hands = [Hand()]

    @classmethod
    def from_dict(cls, data: dict):
        """Gjenoppretter Player og tilhørende Hand-objekter fra JSON-data."""
        raw_hands = data.pop("hands", [])
        hands = [Hand(**h) for h in raw_hands]
        return cls(**data, hands=hands)


@dataclass
class Dealer:
    """Oppretter dealer-instansen."""
    bank: int = 100000
    hole_card: bool = True
    hand: Hand = field(default_factory=Hand)

    def show_hole_card(self):
        """Snur dealerens skjulte kort face-up."""
        if len(self.hand.cards) > 1:
            self.hand.cards[1]["face_down"] = False

    def reset_for_new_round(self):
        self.hand = Hand()

    @classmethod
    def from_dict(cls, data: dict):
        raw_hand = data.pop("hand", {})
        hand = Hand(**raw_hand) if isinstance(raw_hand, dict) else Hand()
        return cls(bank=data.get("bank", 100000), hole_card=data.get("hole_card", True), hand=hand)


@dataclass
class Deck:
    """Håndterer kortstokken (skoen). Generator bygger num_decks komplette sett."""
    num_decks: int = 6
    deck: List[Dict[str, Any]] = field(default_factory=list)
    discards: List[Dict[str, Any]] = field(default_factory=list)

    SUITS = ["Hearts", "Clubs", "Spades", "Diamonds"]
    RANKS = [("2", 2), ("3", 3), ("4", 4), ("5", 5),
             ("6", 6), ("7", 7), ("8", 8), ("9", 9),
             ("10", 10), ("J", 10), ("Q", 10), ("K", 10),
             ("A", 11)]

    def __post_init__(self):
        if not self.deck and not self.discards:
            self.build_deck()
            self.shuffle()

    def build_deck(self):
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
        random.shuffle(self.deck)

    def draw(self):
        """Trekker ett kort. Stokker og bygger ny bunke automatisk dersom skoen blir tom."""
        if not self.deck:
            self.build_deck()
            self.shuffle()
        return self.deck.pop(0) if self.deck else None

    def collect_cards(self, cards: list):
        """Samler inn brukte kort, tilbakestiller face_down og legger dem i stokken."""
        for card in cards:
            card["face_down"] = False
            self.deck.append(card)

    def __len__(self):
        return len(self.deck)


class BlackJack:
    """Hovedspillmotor tilpasset GUI med konfigurerbare hus- og spilerregler."""

    def __init__(self, shoe_size: int = 2):
        # Regelinnstillinger
        self.hole_card = True
        self.shoe_size = shoe_size
        self.infinite_bank = True  # Husets bank er uendelig/begrenset
        self.dealer_stand_threshold = 17  # Standard: 17 (kan settes til 18 for oppgavetekst)
        self.hit_on_soft = False  # Dealer trekker på Soft N (f.eks. Soft 17)
        self.MAX_HANDS = 4  # Maks antall hender tillatt ved splitting
        self.allow_double_after_split = True  # Tillat dobling etter split

        # Tilstander
        self.game_phase = GamePhase.BETTING
        self.current_player_index = 0
        self.current_hand_index = 0
        self.round_summary = ""

        # Opprett instanser
        self.deck = Deck(self.shoe_size)
        self.players = [Player("Player 1")]
        self.dealer = Dealer(hole_card=self.hole_card)

    @property
    def current_player(self) -> Player:
        if 0 <= self.current_player_index < len(self.players):
            return self.players[self.current_player_index]
        return None

    @property
    def current_hand(self) -> Hand:
        player = self.current_player
        if player and 0 <= self.current_hand_index < len(player.hands):
            return player.hands[self.current_hand_index]
        return None

    def reset_game(self, player_name: str = "Player 1", starting_funds: int = 10000):
        """Nullstiller spillet helt etter Game Over."""
        self.players = [Player(name=player_name, funds=starting_funds)]
        self.dealer = Dealer(hole_card=self.hole_card)
        self.deck = Deck(self.shoe_size)
        self.game_phase = GamePhase.BETTING
        self.current_player_index = 0
        self.current_hand_index = 0
        self.round_summary = ""

    def place_bet(self, amount: int, player_index: int = 0) -> bool:
        if 0 <= player_index < len(self.players):
            return self.players[player_index].bet(amount)
        return False

    def start_round(self):
        """Starter runden, deler ut 2 kort og sjekker initial Blackjacks."""
        self.game_phase = GamePhase.DEALING
        self.deck.shuffle()

        for player in self.players:
            player.hands[0].add_card(self.deck.draw())
        self.dealer.hand.add_card(self.deck.draw())

        for player in self.players:
            player.hands[0].add_card(self.deck.draw())
        self.dealer.hand.add_card(self.deck.draw(), face_down=self.hole_card)

        all_done = self.check_initial_blackjacks()
        if all_done:
            self.game_phase = GamePhase.ROUND_OVER
        else:
            self.game_phase = GamePhase.PLAYER_TURN
            self.current_player_index = 0
            self.current_hand_index = 0

    def check_initial_blackjacks(self) -> bool:
        """Sjekker om dealer eller spillere får åpnings-Blackjack."""
        dealer_is_jacked = self.dealer.hand.is_blackjack()

        if dealer_is_jacked:
            self.dealer.show_hole_card()
            for player in self.players:
                player.hands[0].is_done = True
                if player.hands[0].is_blackjack():
                    player.funds += player.hands[0].bet
                else:
                    if not self.infinite_bank:
                        self.dealer.bank += player.hands[0].bet
            self.round_summary = "Dealer has Blackjack!"
            return True

        all_players_jackpot = True
        for player in self.players:
            if player.hands[0].is_blackjack():
                payout = int(player.hands[0].bet * 2.5)
                player.funds += payout
                if not self.infinite_bank:
                    self.dealer.bank -= (payout - player.hands[0].bet)
                player.hands[0].is_done = True
            else:
                all_players_jackpot = False

        return all_players_jackpot

    def hit(self):
        """Trekker ett kort for den aktive hånden."""
        hand = self.current_hand
        if not hand or hand.is_done:
            return

        hand.add_card(self.deck.draw())
        score = hand.get_score()

        if score > 21:
            self.round_summary = f"BUST! {self.current_player.name} exceeded 21!"
            hand.is_done = True
            self.advance_turn()
        elif score == 21:
            hand.is_done = True
            self.advance_turn()

    def stand(self):
        """Står på den aktive hånden og avanserer turen."""
        hand = self.current_hand
        if not hand:
            return

        hand.is_done = True
        self.advance_turn()

    def double_down(self):
        """Dobler innsatsen, trekker nøyaktig ett kort og avslutter hånden."""
        player = self.current_player
        hand = self.current_hand
        if not player or not hand or hand.is_done:
            return

        can_double = (
                player.funds >= hand.bet
                and len(hand.cards) == 2
                and (self.allow_double_after_split or len(player.hands) < 2)
        )

        if can_double:
            player.funds -= hand.bet
            hand.bet *= 2
            hand.is_doubled = True
            hand.add_card(self.deck.draw())
            hand.is_done = True
            self.advance_turn()

    def split(self):
        """Splitter gjeldende hånd dersom vilkårene er oppfylt."""
        player = self.current_player
        hand_idx = self.current_hand_index
        if not player:
            return

        current_hand = player.hands[hand_idx]

        can_split = (
                current_hand.is_splittable()
                and player.funds >= current_hand.bet
                and len(player.hands) < self.MAX_HANDS
        )

        if can_split:
            player.funds -= current_hand.bet
            new_hand = Hand(bet=current_hand.bet)

            split_card = current_hand.cards.pop()
            new_hand.add_card(split_card)

            current_hand.add_card(self.deck.draw())
            new_hand.add_card(self.deck.draw())

            # Lås hender dersom det var Aser som ble splittet
            if split_card.get("rank") == "A":
                current_hand.is_done = True
                new_hand.is_done = True

            # Sett inn den nye hånden FØR advance_turn sjekkes!
            player.hands.insert(hand_idx + 1, new_hand)

            if current_hand and current_hand.is_done:
                self.advance_turn()

    def advance_turn(self):
        """Avanserer til neste hånd, neste spiller eller starter dealerens tur."""
        player = self.current_player
        if not player:
            return

        if self.current_hand_index + 1 < len(player.hands):
            self.current_hand_index += 1
            if self.current_hand.is_done:
                self.advance_turn()
            return

        self.current_hand_index = 0
        self.current_player_index += 1

        if self.current_player_index >= len(self.players):
            self.game_phase = GamePhase.DEALER_TURN
            self.play_dealer_turn()

    def play_dealer_turn(self):
        """Dealer viser kort og trekker basert på stand-grense og Soft-regel."""
        self.dealer.show_hole_card()

        active_hands = [
            hand for player in self.players
            for hand in player.hands
            if hand.get_score() <= 21 and not hand.has_blackjack
        ]

        if active_hands:
            while True:
                score = self.dealer.hand.get_score()
                if score < self.dealer_stand_threshold:
                    self.dealer.hand.add_card(self.deck.draw())
                elif score == self.dealer_stand_threshold and self.hit_on_soft and self.dealer.hand.is_soft():
                    self.dealer.hand.add_card(self.deck.draw())
                else:
                    break

        self.settle_bets()

    def settle_bets(self):
        """Gjennomfører rundoppgjør og regner ut utbetalinger."""
        self.game_phase = GamePhase.EVALUATION
        dealer_score = self.dealer.hand.get_score()
        dealer_busted = dealer_score > 21
        summaries = []

        for player in self.players:
            for i, hand in enumerate(player.hands):
                hand_label = f" (Hand {i + 1})" if len(player.hands) > 1 else ""
                p_score = hand.get_score()

                if p_score > 21:
                    summaries.append(f"{player.name}{hand_label}: BUST ({p_score}) - Lost {hand.bet} D$")
                    if not self.infinite_bank:
                        self.dealer.bank += hand.bet
                    continue

                if hand.has_blackjack:
                    summaries.append(f"{player.name}{hand_label}: BLACKJACK! Won {int(hand.bet * 2.5)} D$")
                    continue

                if dealer_busted:
                    payout = hand.bet * 2
                    player.funds += payout
                    if not self.infinite_bank:
                        self.dealer.bank -= hand.bet
                    summaries.append(f"{player.name}{hand_label}: Dealer Busted! Won {payout} D$")
                elif p_score > dealer_score:
                    payout = hand.bet * 2
                    player.funds += payout
                    if not self.infinite_bank:
                        self.dealer.bank -= hand.bet
                    summaries.append(f"{player.name}{hand_label}: WON ({p_score} vs {dealer_score})! Paid {payout} D$")
                elif p_score == dealer_score:
                    player.funds += hand.bet
                    summaries.append(f"{player.name}{hand_label}: PUSH ({p_score} vs {dealer_score}). Bet returned.")
                else:
                    if not self.infinite_bank:
                        self.dealer.bank += hand.bet
                    summaries.append(
                        f"{player.name}{hand_label}: LOSS ({p_score} vs {dealer_score}). Lost {hand.bet} D$")

        self.round_summary = " | ".join(summaries)
        self.game_phase = GamePhase.ROUND_OVER

    def cleanup_round(self):
        """Samler inn brukte kort og gjør klar til ny runde."""
        if hasattr(self.dealer.hand, "cards"):
            self.deck.collect_cards(self.dealer.hand.cards)
            self.dealer.hand.cards.clear()

        for player in self.players:
            for hand in player.hands:
                self.deck.collect_cards(hand.cards)
            player.reset_for_new_round()

        self.game_phase = GamePhase.BETTING
        self.current_player_index = 0
        self.current_hand_index = 0

    def save_game(self, save_name: str):
        """Lagrer spilltilstanden med alle innstillinger til JSON."""
        if not os.path.exists(SAVES_DIR):
            os.makedirs(SAVES_DIR)

        clean_name = "".join(c for c in save_name if c.isalnum() or c in (" ", "_", "-")).strip()
        if not clean_name:
            clean_name = "quicksave"

        filepath = os.path.join(SAVES_DIR, f"{clean_name}.json")

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
            "game_phase": self.game_phase.value if isinstance(self.game_phase, GamePhase) else self.game_phase,
            "infinite_bank": self.infinite_bank,
            "dealer_stand_threshold": self.dealer_stand_threshold,
            "hit_on_soft": self.hit_on_soft,
            "MAX_HANDS": self.MAX_HANDS,
            "allow_double_after_split": self.allow_double_after_split
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=4)
            return True, filepath
        except Exception as e:
            return False, str(e)

    def load_game(self, filepath: str) -> bool:
        """Laster spilltilstanden fra JSON-fil."""
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.players = [Player.from_dict(player) for player in data.get("players", [])]
            self.dealer = Dealer.from_dict(data.get("dealer", {}))
            self.deck = Deck(**data.get("deck", {})) if data.get("deck") else Deck(self.shoe_size)

            self.current_player_index = data.get("current_player_index", 0)
            self.current_hand_index = data.get("current_hand_index", 0)

            # Gjenopprett regelinnstillinger
            self.infinite_bank = data.get("infinite_bank", True)
            self.dealer_stand_threshold = data.get("dealer_stand_threshold", 17)
            self.hit_on_soft = data.get("hit_on_soft", False)
            self.MAX_HANDS = data.get("MAX_HANDS", 4)
            self.allow_double_after_split = data.get("allow_double_after_split", True)

            raw_phase = data.get("game_phase", "BETTING")
            self.game_phase = GamePhase(raw_phase) if raw_phase in GamePhase.__members__ else GamePhase.BETTING
            return True
        except Exception:
            return False

    @staticmethod
    def get_all_saves():
        """Henter alle lagringsfiler fra saves/-mappen."""
        if not os.path.exists(SAVES_DIR):
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