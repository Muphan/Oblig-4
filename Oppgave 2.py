from classes import BlackJack
""" Importing the class BlackJack form classes.py all game code
is contained there.
classes.py imports the ascii rendering from ascii_renderer.py
ascii_renderer.py imports ascii assets from card_assets.py"""

def main():
    while True:
        game = BlackJack()

        game.run_game()

        query_replay = input("\n\nPress enter to play again, [Q] to quit.").strip().lower()
        if query_replay == "q":
            break


if __name__ == "__main__":
    main()


"""
================================================
Kjøreeksempel:

Har lagt inn metode for ascii render å cleare terminalen,
så eksempelet er litt stykket opp fra forskjellige kjøringer.
================================================
Who shall join us for this round of wagers?
(Press ENTER on a blank line when all players are registered)

State your name, Player 1!
Muphan
Player 2 name (or press ENTER to start):


=== THE TABLE IS SET ===
Muphan, place your wager, mortal! (Funds: 10000)

# better 10000 og gjør ett par hits:
================================================
              --- DEALER (17) ---               
   +-----------+ +-----------+ +-----------+    
   | K         | | 4         | | 3         |    
   |           | |           | |           |    
   |     ♣     | |     ♦     | |     ♥     |    
   |           | |           | |           |    
   |         K | |         4 | |         3 |    
   +-----------+ +-----------+ +-----------+    
------------------------------------------------
   --- MUPHAN | Wager: 10000 | Points: 20 ---   
+-----------+ +-----------+ +-----------+ +-----------+
| 7         | | 2         | | 3         | | 8         |
|           | |           | |           | |           |
|     ♥     | |     ♦     | |     ♣     | |     ♦     |
|           | |           | |           | |           |
|         7 | |         2 | |         3 | |         8 |
+-----------+ +-----------+ +-----------+ +-----------+

================================================

Dealer stands with 17 points!

========================================
            FINAL TALLY            
========================================
Congratulations! Muphan beats dealer!
(20 vs 17)
Muphan won a payout of 20000 D$!
========================================


----------------------------------------
Press [ENTER] to play another round, or [Q]uit to leave the table: 
q

You gather your winnings and step away from the table. Until next time, mortal...


Press enter to play again, [Q] to quit.q

Process finished with exit code 0

================================================
Eksempel på game over:
================================================
              --- DEALER (21) ---               
   +-----------+ +-----------+ +-----------+    
   | 10        | | 4         | | 7         |    
   |           | |           | |           |    
   |     ♠     | |     ♥     | |     ♣     |    
   |           | |           | |           |    
   |        10 | |         4 | |         7 |    
   +-----------+ +-----------+ +-----------+    
------------------------------------------------
   --- MUPHAN | Wager: 25000 | Points: 19 ---   
   +-----------+ +-----------+ +-----------+    
   | 8         | | 8         | | 3         |    
   |           | |           | |           |    
   |     ♦     | |     ♦     | |     ♦     |    
   |           | |           | |           |    
   |         8 | |         8 | |         3 |    
   +-----------+ +-----------+ +-----------+    

================================================

Dealer stands with 21 points!

========================================
            FINAL TALLY            
========================================
LOSS! Dealer beats muphan's hand!
========================================


----------------------------------------
Press [ENTER] to play another round, or [Q]uit to leave the table: 

 muphan has run out of funds, and is cast down into the pits!
            No players left!            

                  THE                   

                 HOUSE                  

                 ALWAYS                 

                  WINS                  


Press enter to play again, [Q] to quit.q

Process finished with exit code 0

"""