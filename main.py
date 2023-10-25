import mysql.connector
from story import get_story
from game import game
from display import clear_screen, print_experience_notification, print_high_score


# ---------------------
# GAME MAIN MENU
# ---------------------
def main(use_online_database, database_config=None):
    # init database connection
    if use_online_database:
        database_config = {"host": "aws.connect.psdb.cloud",
                           "user": "dxqpz25yy8kfdhyfsaja",
                           "password": "pscale_pw_6thKhkwxlyLOrxODDjTP91kJsehBJWJC93ynBxsjFrb",
                           "database": "cargo_carrier",
                           "port": 3306}

    connection = mysql.connector.connect(
        host=database_config["host"],
        port=database_config["port"],
        database=database_config["database"],
        user=database_config["user"],
        password=database_config["password"],
        autocommit=True)

    # notify user to adjust or change to terminal
    print_experience_notification()

    # Give player option to read story or not
    clear_screen()
    while True:
        story = input("Do you want to read background story of this game? (Y/n): ").strip().upper()
        if story == 'N':
            break
        elif story == 'Y' or story == '':  # make Y a default option
            # print(get_story())
            for line in get_story():
                print(line)
            break
        else:
            print("Invalid option! Please enter only 'y' or 'n'")
    print("\n")
    # print("(using offline(local) database)" if use_local_database else "(using online database)")
    print("-" * 80)
    print("Objective: Win €20 000 in 5 days.")
    print("\nRules:")
    print("1. Buy fuel to fly, fly to earn, and keep low emission (calculated for final score)")
    print("2. Make choice when arrival, with risk and reward.")
    print("3. Visit new airports, to find special treasure! (you have a detector)")
    print("-" * 80)
    print("All right! Now let's get starting your journey")
    print("-" * 80)

    while True:
        print("1.New Game\n2.Continue\n3.High Score\n4.Exit")
        select = input("> ").strip()
        if select == "1":
            game(connection)
        elif select == "2":
            game(connection, True)
        elif select == "3":
            print_high_score(connection)
        elif select == "4":
            break
        else:
            print("Invalid option!\n")


# note: end type 1: win. 2: time, 3: fuel and money, 4: coffee
if __name__ == "__main__":
    # use local database or online database
    # if online database is slow or unstable, please use local database instead

    # --- Database Source Config ---
    use_online_database = True
    local_database_config = {"host": "127.0.0.1",
                             "user": "root",
                             "password": "metro",
                             "database": "cargo_carrier",
                             "port": 3306}
    # --- Database Source Config ---

    if use_online_database:
        main(use_online_database)
    else:
        main(use_online_database, local_database_config)
