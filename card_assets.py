RED = "\033[91m"
RESET = "\033[0m"

SUIT_SYMBOLS = {
    "Hearts": f"{RED}♥{RESET}",
    "Diamonds": f"{RED}♦{RESET}",
    "Spades": "♠",
    "Clubs": "♣"
}

FACE_DOWN_CARD = (
    "+===========+",
    "|| + + + + ||",
    "||+ + + + +||",
    "|| + + + + ||",
    "||+ + + + +||",
    "|| + + + + ||",
    "+===========+"
)

CARD_TEMPLATE = (
    "+-----------+",
    "| {rank:<2}        |",
    "|           |",
    "|     {symbol}     |",
    "|           |",
    "|        {rank:>2} |",
    "+-----------+"
)