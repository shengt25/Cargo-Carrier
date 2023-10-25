# Game Description
## Story
In a world of European cargo aviation, you command your own plane. With 30 European airports at your disposal,
you are tasked with delivering cargo from one airport to another. Your mission is clear: efficiently transport goods,
manage your finances, and reach key objective— accumulate 20 000 EURO. Time is your greatest constraint; you have just 5 game days to achieve these goals.
You can get a great tip by company for a good job, but you also risk becoming a victim of competitors who will damage your cargo,
the fine is almost all your money. If you don’t want to take the risk to unload, just pay 200 EURO to hand over to professional unloader.
Remember - airlines really value flying to different airports, this can work to your advantage ;-)
As you take off on your maiden flight, your journey begins. Your choices and strategy will determine your success or failure.
The European skies are yours to navigate, but the path to victory demands cold calculation and skillful decision-making.
## Objective
 Objective: Win €20 000 in 5 days.
## Rules
1. Buy fuel to fly, fly to earn, and keep low emission (calculated for final score)
2. Make choice when arrival, with risk and reward.
3. Visit new airports, to find special treasure! (you have a detector)

# How to play
## Installation
1. **Download the game**  
    `git clone https://github.com/shengt25/flygame.git`
2. **Enter the game directory**  
    `cd flygame`
3. **Run the game**  
    `python3 main.py`
## Game Play
After entering the main menu, you can some options to choose from.
1. **New Game**  
   This will start a new game, and you will be asked to enter your name.
2. **Continue**  
    This will continue your previous game. Note that game will always be saved automatically.  
    So if you didn't finish your last game, you can always continue it.
3. **High Score**  
    This will show the top 10 high scores.
4. **Exit**  
    This will exit the game.

# Game Configuration
## Database Source Configuration (Online/Local)
The game uses an online database to store all game data, including airports information, game progress, and high scores.  
**However, with a free cloud database, the response time is not very good.**  
To have a better experience, you can also use the local database.
### Use the local database
Note: Make sure you have properly started the database server, and imported the database from file `flight_game.sql`
1. Open `main.py`
2. Locate `# --- Database Source Config ---` at the bottom  
3. Change `use_online_database = True` to `use_online_database = False`  
4. Change other parameters in `local_database_config` to your local database server configuration
### Use the online database
The game use online database by default. You don't need to do anything.  
Or if you have changed it to use local database, you can change it back by: setting `use_online_database = True`

## Other Configuration (Advance)
1. Open `game.py`
2. Locate `def game(connection, resume=False, debug=False):`  
3. Change the values defined below there