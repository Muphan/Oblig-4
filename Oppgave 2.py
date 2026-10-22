import classes





def main():
    while True:
        game = classes.BlackJack()

        game.run_game()

        query_replay = input("\n\nPress enter to play again, [Q] to quit.").strip().lower()
        if query_replay == "q":
            break


if __name__ == "__main__":
    main()