from card_assets import SUIT_SYMBOLS, FACE_DOWN_CARD, CARD_TEMPLATE

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