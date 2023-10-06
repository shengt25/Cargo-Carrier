import os
import random
import time
import sys
import mysql.connector

from animation import *
from geopy import distance


# todo round all number to 2 decimal

# ---------------------
# UTILITIES
# ---------------------
def clear_screen():
    """Clear previous text on screen to make it tidy. Not working in IDE."""
    os.system("cls" if os.name == "nt" else "clear")


def database_execute(sql_query, parameter: tuple = None, multiple_response=False):
    """
    Execute sql command and return the result
    :param sql_query: Sql query, replace variable with placeholder "%s"
    :param parameter: Variable in tuple. If only one then: (1, )
    :return:
    """
    # convert to tuple if parameter a single data
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql_query, parameter)
    response = cursor.fetchall()
    return response


def time_real_to_game(time_limit):
    return time_scale * time_limit


def second_to_hms(seconds):
    days = int(seconds / 3600 / 24)  # note: int(0.9) = 0
    hours = int(seconds / 3600 - days * 24)
    minutes = int(seconds / 3600 - hours * 60 - days * 24)
    return days, hours, minutes


# ---------------------
# AIRPORT STUFF
# ---------------------
def generate_random_airports(num: int):
    """
    Generate random airports and save to database, no return.
    :param num: The number of airports desired
    """
    # get random airports
    sql_query = """
    SELECT airport.iso_country, ident, airport.name, country.name as country_name, latitude_deg, longitude_deg
    FROM airport
    JOIN country on airport.iso_country = country.iso_country
    WHERE airport.continent = 'EU'
    AND type = 'large_airport'
    ORDER BY RAND()
    LIMIT %s
    """
    airport_info_list = database_execute(sql_query, (num,))

    # delete last random airports
    sql_query = "DELETE FROM game_airport"
    database_execute(sql_query)

    # save to database
    # todo use sql
    for airport_info in airport_info_list:
        iso_country = airport_info["iso_country"]
        country_name = airport_info["country_name"]
        ident = airport_info["ident"]
        name = airport_info["name"]
        latitude_deg = airport_info["latitude_deg"]
        longitude_deg = airport_info["longitude_deg"]
        sql_query = """INSERT INTO game_airport 
        (iso_country, country_name, ident, name, latitude_deg, longitude_deg, visit) 
        VALUES (%s, %s, %s, %s, %s, %s, 0)"""
        parameter = (iso_country, country_name, ident, name, latitude_deg, longitude_deg)
        database_execute(sql_query, parameter)


def get_airports_distance(first_airport_ICAO, second_airport_ICAO):
    """Calculate distance with two ICAO
    :param first_airport_ICAO: ICAO of first airport
    :param second_airport_ICAO: ICAO of first airport
    :return: Rounded distance (float, with 2 decimal)"""
    sql_query = "SELECT latitude_deg , longitude_deg FROM airport WHERE ident = %s OR ident = %s"
    response = database_execute(sql_query, (first_airport_ICAO, second_airport_ICAO))
    first_airport_coordinates = response[0]["latitude_deg"], response[0]["longitude_deg"]
    second_airport_coordinates = response[1]["latitude_deg"], response[1]["longitude_deg"]

    airports_distance = distance.distance(first_airport_coordinates, second_airport_coordinates).km
    rounded_distance = round(airports_distance, 2)
    return rounded_distance


def get_airports_in_range(player_state) -> list:
    """
    Return airports in order, by distance
    :param player_state: Player state dictionary
    :return: List of dictionary: [{ident, name, country_name, visit, distance, fuel_consumption}, {...}, ...]
    """
    # todo also range in time!!!
    fuel = player_state["fuel"]
    fuel_range = round(fuel / fuel_consumption, 2)
    sql_query = "SELECT ident, name, country_name, visit FROM game_airport"
    airport_info_list = database_execute(sql_query)
    player_ICAO = player_state["location"]
    airports_in_range = []
    for airport_info in airport_info_list:
        dest_ICAO = airport_info["ident"]
        if dest_ICAO != player_ICAO:
            distance = get_airports_distance(player_ICAO, dest_ICAO)
            if distance <= fuel_range:
                airport_info["distance"] = distance
                airport_info["time"] = distance / plane_speed
                airport_info["fuel_consumption"] = distance * fuel_consumption
                airports_in_range.append(airport_info)
    airports_in_range.sort(key=lambda x: x["distance"])
    return airports_in_range


# ---------------------
# PLAYER STATE
# ---------------------
def save_player_state(player_state: dict, init: bool = False):
    """
    Save player state to database. (money, fuel, emission, location, probability, time)
    :param player_state: Player state dictionary
    :param init: Initial saving of a new game?
    """
    if init:
        sql_query = "INSERT INTO game (money, fuel, emission, location, probability, screen_name, time) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    else:
        sql_query = "UPDATE game SET money = %s,fuel=%s, emission=%s, location=%s, probability=%s, time=%s WHERE screen_name IS %s"
    parameter = (player_state["money"], player_state["fuel"], player_state["emission"], player_state["location"],
                 player_state["probability"], player_state["name"], player_state["time"])
    database_execute(sql_query, parameter)


def get_player_state():
    # note: when player has same name, select the newest one (whose id is bigger).
    sql_query = "SELECT money, fuel, emission, location, probability, time FROM GAME WHERE screen_name=%s and id=(SELECT max(id) FROM GAME)"
    player_state2 = database_execute(sql_query, (player_name,))
    return player_state2


def format_player_state(player_state):
    """Returns the player info in formatted string (ready for print). Can be used as header in other info print."""
    a = "^"  # align
    w1 = 10  # width small
    w2 = 15  # width medium
    w3 = 20  # width big
    money = player_state['money']
    fuel = player_state['fuel']
    emission = player_state['emission']
    location = player_state['location']
    probability = str(player_state['probability']) + "%"
    info1 = f"{'Time Left':{a}{w1}} | {'Money':{a}{w1}} | {'Fuel':{a}{w1}} | {'CO2 Emission':{a}{w2}} | {'Location':{a}{w3}} | {'Detector':{a}{w1}}"
    info2 = f"{'HHH MMM':{a}{w1}} | {money:{a}{w1}} | {fuel:{a}{w1}} | {emission:{a}{w2}} | {location:{a}{w3}} | {probability:{a}{w1}}"
    split = "-" * len(info1)
    return "\n".join([split, info1, info2, split])


# ---------------------
# MAIN GAME CODE
# ---------------------


def reception(player_state: dict):
    """
    Player can shop here.
    :param player_state: Player state dictionary
    """
    global coffee_count, wrong_count  # some fun things
    welcome_message = f"Hey {player_name}, welcome! What can I help you with?"
    # print menu, wait for selection, until player choose to leave.
    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)
        print("1. Buy fuel\n2. Continue my journey\n3. Have some coffee")
        select = input("> ")
        if select == "1":  # buy fuel
            welcome_message = "So, preparing to go?"
            print(f"Okay, the price is {fuel_price}/ton, how many do you want?")
            try:
                amount = int(input("> "))
            except:
                print("Hmm, please tell me only numbers.")
                input("(press Enter to continue)")
            else:
                expense = amount * fuel_price
                print(f"That is €{expense} for {amount} ton fuel, is that ok?")
                print("(press Enter to continue, input c to cancel)")
                confirm = input("> ")
                if confirm == "":
                    if player_state["money"] < expense:
                        print("Are you sure? Seems you don't have enough money.")
                        input("(press Enter to continue)")
                    else:
                        # spend money and save to database
                        player_state["money"] -= expense
                        save_player_state(player_state)
                        print("Thank you for purchasing!")
                        input("(press Enter to continue)")
                else:
                    print("Ok, cancelled.")
        elif select == "2":  # leave
            welcome_message = "Hey, welcome back, anything I can do for you?"
            print("Nähdään, see you next time!")
            input("(press Enter to continue)")
            # todo go to next location here
        elif select == "3":  # buy coffee
            welcome_message = "Great coffee, right? What do you need now?"
            if player_state["money"] < 3:
                print("Interesting, you can't even afford a cup of coffee!")
                input("(press Enter to continue)")
            else:
                # spend money and save to database
                player_state["money"] -= 3
                save_player_state(player_state)
                print("You spent €3, had a cup of coffee, feel refreshed, nothing else happened")
                input("(press Enter to continue)")
                coffee_count += 1
        else:  # wrong option
            welcome_message = "Anything else?"
            print("Sorry that is not an option.")
            input("(press Enter to continue)")
            wrong_count += 1


def arrive(airport_icao: str, fuel_last_fly: int, player_state: dict):
    # check is this unvisited airport
    sql_query = "SELECT name, country_name, visit FROM game_airport WHERE ident=%s"
    airport_info = database_execute(sql_query, (airport_icao,))
    airport_name = airport_info[0]['name']
    country_name = airport_info[0]['country_name']
    fuel_back = fuel_back_percent / 100 * fuel_last_fly
    welcome_message = (f"Hello, welcome to {airport_name} in {country_name} (ICAO: {airport_icao})\n"
                       f"Want to try your luck? Just €{dice_game_cost}! If not, "
                       f"I'll return you {fuel_back_percent}% fuel back ({fuel_back} kg), as promised.")
    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)
        print("1. Sure\n2. Tell me about it\n3. Next time")
        select = input("> ")
        if select == "1":  # go dice game
            print("Great! Tell me when you're ready.")
            input("(press Enter to continue)")
            result = random.randint(1, 6)
            play_rolling_dice(result)
            if result == 1:
                dice_message = ""
            elif result == 2:
                dice_message = ""
            elif result == 3:
                dice_message = ""
            elif result == 4:
                dice_message = ""
            elif result == 5:
                dice_message = ""
            else:
                dice_message = ""
            # change player state and save to database.
            # player_state["money"] =
            # save_player_state(player_state)
            print(dice_message)
            input("(press Enter to continue)")

        elif select == "2":  # about game
            print("It is a dice game, roll the dice.\nThe number you get, will decide your destiny:")
            print("\t1:\n"
                  "\t2:\n"
                  "\t3:\n"
                  "\t4:\n"
                  "\t5:\n"
                  "\t6:")
            print("Easy, right?")
            input("(press Enter to continue)")
        elif select == "3":  # leave
            print(f"Ok then, {fuel_back} has been added to your plane, see you next time!")
            break
        else:
            print("Sorry that is not an option.")
            input("(press Enter to continue)")
        welcome_message = f"So, make you decision, €{dice_game_cost} to play or I give you {fuel_back} kg fuel back"


def departure(player_state):
    # todo when don't have any dest, prompt time, or money, or fuel, or fail!
    # todo time=0 when flying? or just don't fly
    a = "<"  # align
    w1 = 25  # width small
    w2 = 55  # width big

    while True:
        header = f"{'Airport (Country)    ✔: Visited':{a}{w2}} {'Distance (Fuel)':{a}{w1}} {'ICAO'}"
        print(format_player_state(player_state))
        print(header)
        print(len(header) * "-")

        airport_info_list = get_airports_in_range(player_state)
        for airport_info in airport_info_list:
            column_1 = f"{airport_info['name']} ({airport_info['country_name']})"
            column_2 = f"{airport_info['distance']} km ({airport_info['fuel_consumption']} kg)"
            column_3 = f"{airport_info['ident']}"
            column_4 = f"{airport_info['time']}"
            is_visited = airport_info['visit']
            if is_visited == 1:
                column_1 = "✔ " + column_1
            else:
                column_1 = "✔  " + column_1

            output = f"{column_1:{a}{w2}} {column_2:{a}{w1}} {column_3:{a}{w1}}"
            print(output)
        print("\nYour next destination, enter ICAO:")
        select = input("> ")

        is_dest = False
        for airport_info in airport_info_list:
            if select == airport_info['ident']:
                is_dest = True
                break
        if not is_dest:
            print("Not a valid destination, try again")
            input("(press Enter to continue)")
        else:
            fuel_need = airport_info['fuel_consumption']
            distance = airport_info['distance']
            dest_name = airport_info['name']
            break
    print(fuel_need, distance, dest_name)
    # play_flying()


if __name__ == "__main__":
    # initiate database connection
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        database="flight_game",
        user="root",
        password="metro",
        autocommit=True,
    )

    # plane
    fuel_consumption = 2  # kg per km
    fuel_price = 20
    plane_speed = 800

    # dice game
    fuel_back_percent = 5  # fuel back if not playing dice game, num%
    dice_game_cost = 20  # cost for playing dice game

    # other
    # coffee_count = 0
    # wrong_count = 0
    time_scale = 1800
    time_limit = 1000  # second: real world time



    # input player name
    print("Hello, what's your name?")
    player_name = input("> ")

    # # set default values
    player_state = {"name": player_name, "money": 11112, "fuel": 2222, "emission": 3333, "location": "EDDV",
                    "probability": 5, "time": 5000}

    print(format_player_state(player_state))
    # generate_random_airports(20)


    # save_player_state(player_state, init=True)
    # generate_random_airports(25)

    arrive("LIEE", 100, player_state)
    reception(player_state)
    departure(player_state)
    # #

    # # save to database
    # print(get_airports_in_range(player_state))
