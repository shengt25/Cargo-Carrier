import os
import time
import sys


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def reception(airport):
    a = "^"  # align
    w = 20  # width
    global coffee_count, wrong_count
    welcome = f"Hey {player_name}, welcome to {airport}. What can I help you with"
    while True:
        clear_screen()
        detection_chance = "20%"
        # read other data
        info1 = f"{'Money':{a}{w}} | {'Fuel':{a}{w}} | {'CO2 Emission':{a}{w}} | {'Treasure Detector':{a}{w}} "
        info2 = f"{money:{a}{w}} | {fuel_balance:{a}{w}} | {emission:{a}{w}} | {detection_chance:{a}{w}}"
        split = "-" * len(info1)
        print("\n".join([split, info1, info2, split]))
        print("\n".join([welcome, "1. Buy fuel", "2. Bye", "3. Have some coffee"]))
        select = input("> ")
        if select == "1":
            print(f"Okay, the price is {fuel_price}/ton, how many do you want?")
            try:
                amount = int(input("> "))
            except:
                input("Hmm, please tell me only numbers. (press enter to continue)")
            else:
                expense = amount * fuel_price
                print(f"That is {expense} euros for {amount} ton fuel, is that ok?")
                print("(press enter to continue, input c to cancel)")
                confirm = input("> ")
                if confirm == "":
                    if money < expense:
                        input("Are you sure? seems you don't have enough money. (press enter to continue)")
                    else:
                        input("Thank you for purchasing! (press enter to continue)")
                        # todo deduct money
                else:
                    print("Ok, cancelled.")
        elif select == "2":
            input("Nähdään, see you next time! (press enter to continue)")
            break
        elif select == "3":
            if money < 3:
                input("Interesting, you can't even afford a cup of coffee!. (press enter to continue)")
            else:
                input(
                    "You spent 3 euros, had a cup of coffee, feel refreshed, nothing else happened. (press enter to continue)")
                # todo money - 3
                coffee_count += 1
        else:
            input("Sorry that is not an option. (press enter to continue)")
            wrong_count += 1
        welcome = "Anything else?"


def go_menu_task():
    pass


def arrive():
    pass


def go_menu_main():
    print("")


def get_player_info():
    a = "^"  # align
    w = 20  # width
    detection_chance = "20%"
    info1 = f"{'Money':{a}{w}} | {'Fuel':{a}{w}} | {'CO2 Emission':{a}{w}} | {'Treasure Detector':{a}{w}} "
    info2 = f"{money:{a}{w}} | {fuel_balance:{a}{w}} | {emission:{a}{w}} | {detection_chance:{a}{w}}"
    split = "-" * len(info1)
    return "\n".join([split, info1, info2, split])


def game():
    print("Hello Message")
    is_flying = False

    while True:
        if not is_flying:
            go_menu_main()


if __name__ == "__main__":
    player_name = "NEO"
    money = 1000
    fuel_balance = 10000
    emission = 0

    fuel_price = 10
    coffee_count = 0
    wrong_count = 0
    #
    # player = Player(name="player1", init_money=10000, init_emission=100, init_fuel=100)
    # plane = Plane(player, plane1_specs_list)
    # # player_info()
    #
    # go_menu_shop()
    # plane_flying()
    # plane_flying()
    reception("ad")
