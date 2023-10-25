import mysql.connector
from story import get_story
from game import game
from display import clear_screen, print_experience_notification, print_high_score


# ---------------------
# GAME MAIN MENU
# ---------------------
def main(use_local_database):
    # init database connection
    if use_local_database:
        db_host = "127.0.0.1"
        db_name = "root"
        db_password = "metro"
    else:
        db_host = "aws.connect.psdb.cloud"
        db_name = "msivnka4jfbpdrj18yut"
        db_password = "pscale_pw_4Nc4vK7Qjjl0SUgtQr6q9iCM3isIu3LVm7wAnWpq9T2"

    connection = mysql.connector.connect(
        host=db_host,
        port=3306,
        database="flight_game",
        user=db_name,
        password=db_password,
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

    use_local_database = False
    main(use_local_database)
