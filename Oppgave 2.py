import classes



while True:
    game = classes.BlackJack()

    game.run_game()

    query_replay = input("\n\nPress enter to play again, [Q] to quit.").strip().lower()
    if query_replay == "q":
        break

def main