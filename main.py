import os
import time
from game_elements import *
from utils import *
import sys


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def go_menu_shop_fuel_emission(select):
    flag_buy_fuel = False
    flag_buy_emission = False
    is_success = False
    if select == "1":
        flag_buy_fuel = True
        price = price_data["fuel"]
    else:
        flag_buy_emission = True
        price = price_data["emission"]
    try:
        print(f"Okay, the price is {price}/L, how many litres do you want?")
        amount = int(input("> "))
    except:
        input("Hmm, tell me only numbers, would you? (press enter to continue)")
    else:
        print(f"That is {amount * price} for {amount} litres totally, is that ok?")
        print("(press enter to continue, input c to cancel)")
        confirm = input("> ")
        if confirm == "":
            if flag_buy_fuel:
                is_success = player.buy_fuel(amount)
            elif flag_buy_emission:
                is_success = player.buy_emission(amount)
            if not is_success:
                input("Are you sure? seems you don't have enough money. (press enter to continue)")
            else:
                input("Thank you for purchasing! (press enter to continue)")
        else:
            print("Ok, cancelled.")


def upgrade_plane():
    print("under construction")


def go_menu_shop():
    welcome = f"Hey {player.name}, welcome to my store. What would you like to buy today?"
    while True:
        clear_screen()
        print(get_player_info_formatted())
        print("\n".join([welcome,
                         "1. Fuel",
                         "2. Emission permission",
                         "3. Upgrade my plane",
                         "4. Exit"]))
        select = input("> ")
        if select == "1" or select == "2":
            go_menu_shop_fuel_emission(select)
        elif select == "3":
            upgrade_plane()
        elif select == "4":
            input("Bye, see you next time! (press enter to continue)")
            break
        else:
            input("Sorry that is not an option. (press enter to continue)")
        welcome = "Anything else?"


def go_menu_task():
    pass


def go_menu_main():
    print("")


def get_player_info_formatted():
    player_name = player.name
    game_time = 1000
    # player's data
    player_money = f"Money: {player.money}"
    player_fuel = f"Fuel: {player.fuel}L"
    player_emission = f"CO2 permission: {player.emission}L"

    # plane's data
    plane_emission = f"CO2: {plane.emission}L/km"
    plane_fuel = f"Fuel: {plane.fuel}L/km"
    plane_speed = f"Speed: {plane.speed}km/h"
    plane_payload = f"payload: {plane.payload}ton"

    plane_cargo = ""

    a = "^"
    w = 20
    info = (f"Time left: {game_time} hours\n"
            f"{player_name:{a}{w}} | {player_money:{a}{w}} | {player_fuel:{a}{w}} | {player_emission:{a}{w}}\n"
            f"{'plane specs':{a}{w}} | {plane_emission:{a}{w}} | {plane_fuel:{a}{w}} | {plane_speed:{a}{w}} | {plane_payload:{a}{w}}\n"
            f"{'plane specs':{a}{w}} | {plane_emission:{a}{w}} | {plane_fuel:{a}{w}} | {plane_speed:{a}{w}} | {plane_payload:{a}{w}}\n"
            f"------------------------------------------------")
    return info


def calculate_distance():
    pass


# def plane_flying(start_name, dest_name, distance, plane):
def plane_flying():
    # todo update input here
    time_limit_game = 7200

    start_name = "Helsinki"
    dest_name = "Paris"
    distance = 2000
    speed = 950

    eta_game = (distance / speed) * 60  # time in game (minutes)
    eta_real = eta_game * 60 / time_scale  # time in real world (second)

    # animation
    frame_rate = 40
    interval = 1 / frame_rate
    ani_path_length = 120
    ani_speed_frame = ani_path_length / eta_real / frame_rate  # block speed per frame
    plane_icon = "🛫"

    count = 0
    time_game_frame = time_scale / 60 / frame_rate

    while True:
        pre = int(count * ani_speed_frame)
        suf = int((ani_path_length - (ani_speed_frame * count)))
        animation = start_name + " " * pre + plane_icon + " " * suf + dest_name + " " * 10
        time.sleep(interval)
        count += 1
        time_limit_game -= time_game_frame
        clear_screen()

        print(eta_game, "minutes")
        print("time left:", int(time_limit_game), "minutes")
        print(animation)
        if pre >= ani_path_length:
            break


def plane_landed():
    pass


def generate_location(cities_list, location_min, location_max):
    pass


def generate_cargo():
    pass


def generate_task():
    pass


def accept_task():
    pass


def game():
    print("Hello Message")
    is_flying = False

    while True:
        if not is_flying:
            go_menu_main()


if __name__ == "__main__":
    time_limit = 720  # minutes

    player = Player(name="player1", init_money=10000, init_emission=100, init_fuel=100)
    plane = Plane(player, plane1_specs_list)
    # player_info()

    go_menu_shop()
    plane_flying()
