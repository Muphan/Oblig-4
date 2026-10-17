from card_assets import SUIT_SYMBOLS, FACE_DOWN_CARD, CARD_TEMPLATE
import re
import shutil


### Vibecoded
def center_ansi(text, width):
    # Fjerner ANSI-koder kun for å beregne synlig lengde
    visible_length = len(re.sub(r'\033\[[0-9;]*m', '', text))
    padding = max(0, width - visible_length)
    left_padding = padding // 2
    right_padding = padding - left_padding
    return " " * left_padding + text + " " * right_padding

def display_table(dealer, players):
    # Henter gjeldende terminalbredde (f.eks. 80 eller 120 tegn wide)
    width = shutil.get_terminal_size((80, 20)).columns

    print("\n" + "=" * width)

    # --- 1. DEALER (Sentrert i topp) ---
    dealer_score = dealer.hand.get_score() if hasattr(dealer.hand, "get_score") else ""
    dealer_title = f"--- DEALER ({dealer_score}) ---" if dealer_score else "--- DEALER ---"
    print(center_ansi(dealer_title, width))

    dealer_cards_str = render_cards(dealer.hand.cards)
    if dealer_cards_str:
        for line in dealer_cards_str.split("\n"):
            print(center_ansi(line, width))

    print("-" * width)

    # --- 2. SPILLERE (Håndterer N-hender per spiller) ---
    for player in players:
        for i, hand in enumerate(player.hands):
            # Viser kun "Hånd X" hvis spilleren faktisk har flere enn 1 hånd
            hand_label = f" (Hand {i + 1})" if len(player.hands) > 1 else ""
            player_title = f"--- {player.name.upper()}{hand_label} | Wager: {hand.bet} | Points: {hand.get_score()} ---"
            print(center_ansi(player_title, width))

            player_cards_str = render_cards(hand.cards)
            if player_cards_str:
                for line in player_cards_str.split("\n"):
                    print(center_ansi(line, width))
            print()  # Litt luft under hver hånd

    print("=" * width + "\n")
### ^Vibecoded

def render_cards(cards):
    if not cards: # checks to save resources if cards = [] or None
        return ""

    rendered_list = []
    for card in cards:
        if not card.get("face_down", False):
            suit = card["suit"]
            rank = card["rank"]
            symbol = SUIT_SYMBOLS.get(suit, suit)

            card_lines = tuple(line.format(rank=rank, symbol=symbol) for line in CARD_TEMPLATE)
            rendered_list.append(card_lines)

        else:
            rendered_list.append(FACE_DOWN_CARD)

    lines = [" ".join(line_group) for line_group in zip(*rendered_list)]
    return "\n".join(lines)

def display_cards(cards):
    rendered_output = render_cards(cards)
    if rendered_output:
        print(rendered_output)