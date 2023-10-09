import mysql.connector
import sys, os
from animation import *
from geopy.distance import distance as geo_distance  # prevent shadow_name warning (distance is name of variable)
from story import get_story


# ---------------------
# UTILITIES
# ---------------------
def clear_screen():
    """Clear previous text on screen to make it tidy. NOTE: Please use terminal, because it may not work in IDE."""
    os.system("cls" if os.name == "nt" else "clear")


def database_execute(connection, sql_query, parameter: tuple = None) -> dict:
    """
    Execute sql command and return the result
    :param connection: SQL connection.
    :param sql_query: Sql query, replace variable with placeholder "%s"
    :param parameter: Variable in tuple. If only one then: (1, )
    :return: Dict type response
    """
    # convert to tuple if parameter a single data
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql_query, parameter)
    response = cursor.fetchall()
    return response


def second_to_hm(seconds: int) -> tuple[int, int]:
    """
    :param seconds: Time limit in seconds
    :return: Time limit in hh, mm, ss
    """
    # note: int won't round, eg: int(0.9) = 0
    hour = int(seconds / 3600)
    minute = int(seconds / 60 - hour * 60)
    return hour, minute


def second_to_dhm(seconds: int) -> tuple[int, int, int]:
    """
    :param seconds: Time limit in seconds
    :return: Time limit in hh, mm, ss
    """
    # note: int won't round, eg: int(0.9) = 0
    day = int(seconds / 3600 / 24)
    hour = int(seconds / 3600 - day * 24)
    minute = int(seconds / 60 - hour * 60 - day * 24 * 60)
    return day, hour, minute


def notify_experience():
    try:
        terminal_width = os.get_terminal_size()[0]
    except:
        terminal_width = -1
    try:
        is_idle = "idlelib" in sys.modules
    except:
        print("e")
        is_idle = True
    if terminal_width < 0:
        print("Please use terminal environment for a better experience, thank you!")
    if 0 < terminal_width < 120:
        print("Please adjust your terminal width wider than 120 for a better experience, thank you!")
    if is_idle:
        print("Please use terminal environment for a better experience, thank you!")
    input("(press Enter to continue)")


# ---------------------
# AIRPORT
# ---------------------
def generate_random_airports(connection, num: int) -> dict:
    """
    Generate random airports and save to database, no return.
    :param connection: SQL connection
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
    airport_info_dict = database_execute(connection, sql_query, (num,))

    # delete last random airports
    sql_query = "DELETE FROM game_airport"
    database_execute(connection, sql_query)
    home_airport = None
    # save to database
    # the first airport is home
    home_marked = False
    for airport_info in airport_info_dict:
        if not home_marked:
            sql_query = """INSERT INTO game_airport 
            (iso_country, country_name, ident, name, latitude_deg, longitude_deg, visit) 
            VALUES (%s, %s, %s, %s, %s, %s, 2)"""
            home_marked = True
            home_airport = airport_info
        else:
            sql_query = """INSERT INTO game_airport 
            (iso_country, country_name, ident, name, latitude_deg, longitude_deg, visit) 
            VALUES (%s, %s, %s, %s, %s, %s, 0)"""
        parameter = (
            airport_info["iso_country"], airport_info["country_name"], airport_info["ident"], airport_info["name"],
            airport_info["latitude_deg"], airport_info["longitude_deg"])
        database_execute(connection, sql_query, parameter)
        home_airport["visit"] = 2
    return home_airport


def get_airports_distance(connection, first_airport_icao: str, second_airport_icao: str) -> float:
    """Calculate distance with two ICAO
    :param connection: SQL connection
    :param first_airport_icao: ICAO of first airport
    :param second_airport_icao: ICAO of first airport
    :return: Rounded distance (float, with 2 decimal)"""
    sql_query = "SELECT latitude_deg , longitude_deg FROM airport WHERE ident = %s OR ident = %s"
    response = database_execute(connection, sql_query, (first_airport_icao, second_airport_icao))
    first_airport_coordinates = response[0]["latitude_deg"], response[0]["longitude_deg"]
    second_airport_coordinates = response[1]["latitude_deg"], response[1]["longitude_deg"]

    airports_distance = geo_distance(first_airport_coordinates, second_airport_coordinates).km
    return round(airports_distance)


def get_airports_in_range(connection, plane_param, player_state: dict) -> tuple[dict, list, list, bool]:
    """
    Return airports in order, by distance
    :param plane_param: Plane's fuel, speed, etc.
    :param connection: SQL connection
    :param player_state: Player state dictionary
    :return: List of dictionary: [{ident, name, country_name, visit, distance, fuel_consumption}, {...}, ...]
    """
    fuel = player_state["fuel"]
    range_by_fuel = round(fuel / plane_param["fuel_consumption"])
    range_by_time = round(plane_param["speed"] * player_state["time"] / 3600)
    # plane_speed: km/h ==> plane_speed/3600: km/s

    sql_query = "SELECT ident, name, country_name, visit FROM game_airport"
    airport_info_list = database_execute(connection, sql_query)
    player_icao = player_state["location"]
    airports_in_range = []
    airports_out_of_range = []
    airport_now = None

    # assume no time to fly anywhere, will check is it true, later.
    flag_no_time = True

    for airport_info in airport_info_list:
        dest_icao = airport_info["ident"]
        if dest_icao == player_icao:
            airport_now = airport_info
        else:
            distance = get_airports_distance(connection, player_icao, dest_icao)
            airport_info["distance"] = distance
            airport_info["time"] = round(distance / plane_param["speed"] * 3600)  # time is in second
            airport_info["fuel_consumption"] = round(distance * plane_param["fuel_consumption"])
            airport_info["emission"] = round(distance * plane_param["emission"] / 1000)
            airport_info["reward"] = round(airport_info["distance"] * plane_param["reward"])

            if distance <= range_by_fuel and distance <= range_by_time:
                # if anywhere is in range of time, then there's time to fly somewhere, so, set flag_no_time to False
                if distance <= range_by_time and flag_no_time is True:
                    flag_no_time = False
                airports_in_range.append(airport_info)
            else:
                airports_out_of_range.append(airport_info)
    airports_in_range.sort(key=lambda x: x["distance"])
    return airport_now, airports_in_range, airports_out_of_range, flag_no_time


def mark_visit_airport(connection, selected_airport):
    if selected_airport["visit"] == 0:
        sql_query = "UPDATE game_airport SET visit=1 WHERE ident=%s"
        database_execute(connection, sql_query, (selected_airport["ident"],))


def format_airport_list(airport_list: list, plane_param, airport_now=False) -> list:
    a = "<"  # align to left
    w1 = 8  # align width small
    w2 = 20  # align width medium
    w3 = 55  # align width big
    output_list = []
    for airport_info in airport_list:
        if airport_now:
            # airport now at
            column_name = f"{airport_info['name']} ({airport_info['country_name']})"
            column_icao = f"{airport_info['ident']}"
            if airport_info['visit'] == 1:
                column_name = "✔ " + column_name
            elif airport_info['visit'] == 2:
                column_name = "* " + column_name
            else:
                raise Exception("You are at here but not visit? This is a bug.")
            output = (f"{column_name:{a}{w3}} {column_icao:{a}{w1}} {'-':{a}{w2}} {'-':{a}{w1}} "
                      f"{'-':{a}{w1}} {'-':{a}}")
        else:
            # other airports
            hh, mm = second_to_hm(airport_info["time"])
            column_name = f"{airport_info['name']} ({airport_info['country_name']})"
            column_distance = f"{airport_info['distance']} km ({airport_info['fuel_consumption']} kg)"
            column_icao = f"{airport_info['ident']}"
            column_eta = f"{hh}h {mm}m"
            column_reward = f"€{airport_info['reward']}"
            column_emission = f"{airport_info['emission']} kg"
            # home, visited or not
            if airport_info['visit'] == 1:
                column_name = "✔ " + column_name
            elif airport_info['visit'] == 2:
                column_name = "* " + column_name
            else:
                column_name = "  " + column_name
            output = (f"{column_name:{a}{w3}} {column_icao:{a}{w1}} {column_distance:{a}{w2}} {column_eta:{a}{w1}} "
                      f"{column_reward:{a}{w1}} {column_emission:{a}}")

        output_list.append(output)
    return output_list


# ---------------------
# PLAYER STATE
# ---------------------
def save_player_state(connection, player_state: dict) -> None:
    """
    Save player state to database. (money, fuel, emission, location, probability, time)
    :param connection: SQL connection
    :param player_state: Player state dictionary
    """
    sql_query = ("UPDATE game SET money=%s, fuel=%s, emission=%s, location=%s, probability=%s, "
                 "treasure=%s, time=%s, score=%s, finish=%s "
                 "WHERE screen_name=%s AND id=(SELECT MAX(id) from game WHERE screen_name=%s)")

    parameter = (player_state["money"], player_state["fuel"], player_state["emission"], player_state["location"],
                 player_state["probability"], player_state["treasure"], player_state["time"], player_state["score"],
                 player_state["finish"], player_state["name"], player_state["name"])
    database_execute(connection, sql_query, parameter)


def init_player_state(connection, player_state: dict) -> None:
    sql_query = (
        "INSERT INTO game (money,fuel,emission,location,probability,treasure,time,screen_name,finish,score) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, 0)")
    parameter = (player_state["money"], player_state["fuel"], player_state["emission"], player_state["location"],
                 player_state["probability"], player_state["treasure"], player_state["time"], player_state["name"])
    database_execute(connection, sql_query, parameter)


def load_player_state(connection, player_name: str) -> dict:
    """
    Get player's data from database, and determine whether player has finished game last time
    :param connection: SQL connection
    :param player_name: Player's name
    :return: Player's state, whether finished last game
    """
    # note: when player has same name, select the newest one (whose id is bigger).
    sql_query = ("SELECT money, fuel, emission, location, probability, time, finish, score, treasure FROM game "
                 "WHERE screen_name=%s AND finish=0 AND id=(SELECT max(id) FROM game)")
    player_state = database_execute(connection, sql_query, (player_name,))[0]
    # reset goal reminder if player load game
    player_state["reminder"] = 0
    return player_state


# ---------------------
# GOAL
# ---------------------
def goal_reminder(player_state: dict):
    print(format_player_state(player_state))
    print("Congratulations! You already have enough money for expanding your airport!")
    print("You can choose go home airport or continue earning money (or losing money).")
    print("But be careful with time... and your money")
    print(f"Anyway, you can always make your choice.")

    print("\nYou can now choose EXPAND MY AIRPORT at home, to finish game ")
    print("Your home airport is marked with *")
    input("(press Enter to continue)")


def get_highest_score(connection):
    sql_query = "SELECT max(score) FROM game"
    high_score = database_execute(connection, sql_query)
    return high_score[0]["max(score)"]


def print_high_score(connection):
    sql_query = ("SELECT screen_name, money, fuel, emission, time, "
                 "treasure, score FROM game ORDER BY score DESC LIMIT 10")
    data_dict = database_execute(connection, sql_query)
    a = "^"  # align to center
    w1 = 12  # align width small
    w2 = 15  # align width medium
    header = (f"{'Name':{a}{w1}} | {'Score':{a}{w1}} | {'Money':{a}{w1}} | {'Fuel':{a}{w1}} | "
              f"{'CO2 Emission':{a}{w2}} | {'Time Left':{a}{w2}} | {'Treasure':{a}{w1}}")
    print(header)
    for data in data_dict:
        name = data["screen_name"]
        money = data["money"]
        fuel = data["fuel"]
        emission = data["emission"]
        score = data["score"]

        dd, hh, mm = second_to_dhm(data["time"])
        time_left = f"{dd}d {hh}h {mm}m"
        treasure = data["treasure"]
        if treasure == 1:
            treasure_status = "Found"
        else:
            treasure_status = "Not found"
        data = (f"{name:{a}{w1}} | {score:{a}{w1}} | {money:{a}{w1}} | {fuel:{a}{w1}} | "
                f"{emission:{a}{w2}} | {time_left:{a}{w2}} | {treasure_status:{a}{w1}}")
        print(data)
    return


def calculate_score(player_state, score_param):
    score_money = round(score_param["money"] * player_state["money"])
    score_emission = round(score_param["emission"] * player_state["emission"])
    score_time = round(score_param["time"] * player_state["time"])
    score = score_money + score_time - score_emission
    player_state["score"] = score
    score_dict = {"money": score_money, "time": score_time, "emission": score_emission}
    return score_dict, score


def end_game(end_type):
    # end type 1: win. 2: time, 3: fuel and money, 4: coffee
    if end_type == 1:
        play_win()
    elif end_type == 2:
        play_time_ending()
    elif end_type == 3:
        play_money_ending()
    elif end_type == 4:
        play_coffee_ending()
    else:
        raise Exception("Ending not defined")


# ---------------------
# MAIN GAME MODULE
# ---------------------


def arrive(current_airport_info: dict, plane_param: dict, before_shop_param: dict, player_state: dict):
    """
    Player detects treasure and play dice game here.
    :param current_airport_info:
    :param plane_param:
    :param before_shop_param:
    :param player_state:
    :return:
    """
    # check is this unvisited airport
    airport_name = current_airport_info['name']
    country_name = current_airport_info['country_name']
    distance_last_fly = current_airport_info['distance']

    # set up bonus
    fuel_back_percent = round(
        distance_last_fly / before_shop_param["dividend"] * before_shop_param["fuel_bonus_percent"] + before_shop_param[
            "fuel_base_percent"], 2)
    fuel_back = round(fuel_back_percent * distance_last_fly * plane_param["fuel_consumption"] / 100)

    dice_bonus_percent = round(distance_last_fly / before_shop_param["dividend"], 2)

    # detect treasure when it is not yet done
    if player_state["treasure"] == 0:
        probability_up = 0
        if current_airport_info['visit'] == 0:
            # set up probability, round to int, (use num ‰)
            probability_bonus = distance_last_fly / before_shop_param["dividend"] * before_shop_param[
                "detector_bonus_per_thousand"]
            probability_up = round(before_shop_param["detector_base_per_thousand"] + probability_bonus)
            player_state["probability"] += probability_up

        detection = random.randint(1, 1000)
        if detection <= player_state["probability"]:
            # detected
            player_state["money"] += before_shop_param["treasure_value"]
            player_state["treasure"] = 1
            player_state["probability"] = -1
            play_detector(player_state, probability_up, True)
        else:
            # not detected
            play_detector(player_state, probability_up, False)
    # fix update current airport ICAO
    player_state['location'] = current_airport_info['ident']
    welcome_message = (f"Hello, welcome to {airport_name} in {country_name} (ICAO: {player_state['location']})\n\n"
                       f"Wanna try your luck? Just €{before_shop_param['dice_game_cost']}! "
                       f"If not, I'll return you {fuel_back_percent}% ({fuel_back} kg) fuel back, as promised.\n"
                       f"(reward +{dice_bonus_percent}% based on last flight distance)\n")

    # change welcome message when at home
    if current_airport_info['visit'] == 2:
        welcome_message.replace("Hello, welcome to", "Welcome home, ")
    # dice game
    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)
        print("1. Sure\n2. Tell me about it\n3. Next time")
        select = input("> ")
        if select == "1":  # go dice game
            # fixing subtract 20euro when rolling the dice
            player_state["money"] -= 20
            print("Great! Tell me when you're ready.")
            input("(press Enter to continue)")
            result = random.randint(1, 6)
            play_rolling_dice(player_state, result)
            if result == 1:
                dice_message = "Oh! You lost almost all your money!!! Better luck next time!"
                player_state["money"] = 100
            elif result == 2:
                dice_message = "Bad news, you lost €900!"
                player_state["money"] -= 900
                if player_state["money"] < 0:
                    player_state["money"] = 0
            elif result == 3:
                dice_message = "Well, nothing happened to you."
            elif result == 4:
                earned = 500 + round(500 * dice_bonus_percent / 100)
                dice_message = f"Wow! You earned €{earned} (with {dice_bonus_percent}% bonus)"
                player_state["money"] += earned
            elif result == 5:
                earned = 500 + round(800 * dice_bonus_percent / 100)
                dice_message = f"Great! You earned €{earned} (with {dice_bonus_percent}% bonus)"
            else:
                multiply = 2 + round(2 * dice_bonus_percent / 100, 2)
                dice_message = f"Big one!!! MONEY * {multiply} (with {dice_bonus_percent}% bonus)"
                player_state["money"] = round(player_state["money"] * multiply)
            print(dice_message)
            input("(press Enter to continue)")
            break
        elif select == "2":  # about game
            print("It is a dice game, roll the dice.\nThe number you get, will decide your destiny.")
            print(f"\t1: Lost almost all money. (I will leave you €100)\n"
                  f"\t2: Deduct €900 \n"
                  f"\t3: Nothing will happen\n"
                  f"\t4: Add €{500 + round(500 * dice_bonus_percent / 100)} (with {dice_bonus_percent}% bonus)\n"
                  f"\t5: Add €{800 + round(800 * dice_bonus_percent / 100)} (with {dice_bonus_percent}% bonus)\n"
                  f"\t6: Money multiply {2 + round(2 * dice_bonus_percent / 100, 2)} (with {dice_bonus_percent}% bonus)")
            print("Easy, right?")
            input("(press Enter to continue)")
        elif select == "3":  # leave
            print(f"Ok then, {fuel_back} kg fuel has been added to your plane!")
            # fix update fuel when player get fuel back
            player_state['fuel'] += fuel_back
            break
        else:
            print("Sorry that is not an option.")
            input("(press Enter to continue)")
        welcome_message = (f"So, make you decision, €{before_shop_param['dice_game_cost']} to play "
                           f"or I give you {fuel_back} kg fuel back")


def shop(player_state: dict, current_airport_info: dict, shop_param: dict) -> int:
    """
    Player can shop fuel, coffee, or achieve goal(only at home) here.
    :param player_state: Player state dictionary
    :param current_airport_info:
    :param shop_param:
    :return: Game ending type: 1: win. 2: time, 3: fuel and money, 4: coffee

    """
    # check player's money and send reminder if meet goal
    if player_state["money"] > shop_param['win_money'] and player_state["reminder"] == 0:
        goal_reminder(player_state)
        player_state["reminder"] = 1

    coffee_count = 0  # for fun
    welcome_message = f"Ok {player_state['name']}, what else can I help?\n"
    # print menu, wait for selection, until player choose to leave.
    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)

        # at home
        if current_airport_info["visit"] == 2:
            print("1. Buy fuel\n2. Continue my journey\n3. Have some coffee\n4. Expand my airport")
        else:
            print("1. Buy fuel\n2. Continue my journey\n3. Have some coffee")
        select = input("> ")
        if select == "1":  # buy fuel
            welcome_message = "So, preparing to go?"
            print(f"Okay, the price is {shop_param['fuel_price']}/ton, how many do you want?")
            try:
                amount = int(input("> "))
            except:
                print("Hmm, please tell me only numbers.")
                input("(press Enter to continue)")
            else:
                expense = amount * shop_param['fuel_price']
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
                        # fix update fuel state when purchasing more
                        player_state["fuel"] += amount
                        print("Thank you for purchasing!")
                        input("(press Enter to continue)")
                else:
                    print("Ok, cancelled.")
        elif select == "2":  # leave
            print("Nähdään, see you next time!")
            input("(press Enter to continue)")
            break
        elif select == "3":  # buy coffee
            welcome_message = "Great coffee, right? What do you need now?"
            if player_state["money"] < 3:
                print("Interesting, you can't even afford a cup of coffee!")
                input("(press Enter to continue)")
            else:
                player_state["money"] -= 3
                coffee_count += 1
                if coffee_count >= 10:
                    return 4
                else:
                    print("You spent €3, had a cup of coffee, feel refreshed, nothing else happened")
                    input("(press Enter to continue)")
        elif select == "4" and current_airport_info["visit"] == 2:
            if player_state["money"] < shop_param["win_money"]:
                print("Well, you don't have enough money.")
                print("Reminder:")
                print(f"Your main goal is to earn €{shop_param['win_money']} to expand your airport.")
                print(f"But now you only have €{player_state['money']}, come back later.")
                input("(press Enter to continue)")
            else:
                return 1  # game won!

        else:  # wrong option
            welcome_message = "Anything else?"
            print("Sorry that is not an option.")
            input("(press Enter to continue)")
    return 0


def departure(connection, current_airport_info, shop_param, plane_param, player_state: dict) -> tuple[int, dict]:
    """
    :param shop_param:
    :param current_airport_info:
    :param connection:
    :param plane_param:
    :param player_state:
    :return: Ending type(except for 0), Info of next airport. If
    """
    a = "<"  # align to left
    w1 = 8  # align width small
    w2 = 20  # align width medium
    w3 = 55  # align width big

    welcome_message = "Ready for working? Choose your next cargo destination from the list and get ready for takeoff!\n"
    header = (f"{'Airport (Country)    ✔: Visited    *:Home':{a}{w3}} "
              f"{'ICAO':{a}{w1}} {'Distance (Fuel)':{a}{w2}} {'ETA':{a}{w1}} {'Reward':{a}{w1}} {'Emission':{a}}")
    split_header = len(header) * "-"

    split_here = "You Are Here"
    split_out = f"{'Out of Reach':.<{len(header)}}"
    split_available = f"{'Available':.<{len(header)}}"
    airport_now, airport_avail_list, airport_out_list, flag_no_time = get_airports_in_range(connection, plane_param,
                                                                                            player_state)
    airport_avail_detail_list = format_airport_list(airport_avail_list, plane_param)
    airport_out_detail_list = format_airport_list(airport_out_list, plane_param)
    airport_now_detail = format_airport_list([airport_now], plane_param, True)[0]

    while True:
        print(format_player_state(player_state))
        print(welcome_message)
        print("\n")
        print(header)
        print(split_header)
        print(split_here)
        print(airport_now_detail)
        print(split_available)
        for airport_detail in airport_avail_detail_list:
            print(airport_detail)
        print(split_out)
        for airport_detail in airport_out_detail_list:
            print(airport_detail)

        # if nowhere to go
        if not airport_avail_list:
            # game end: no time
            if flag_no_time:
                return 2, {}
            else:
                # check can player still go anywhere if you use all money to buy fuel.
                # if not, then fail, otherwise reminder player go to shop.
                player_state_temp = copy.deepcopy(player_state)
                player_state_temp["fuel"] += round(player_state_temp["money"] / shop_param["fuel_price"])
                _, airport_info_list_temp, _, _ = get_airports_in_range(connection, plane_param, player_state_temp)
                if not airport_info_list_temp:
                    return 3, {}
                else:
                    print("You don't have enough fuel, but still have some money,")
                    print("Why not going back to shop and buy some?")

        print("\nYour next destination, enter ICAO, or enter s to go back shop:")
        select = input("> ")

        # go back to shop when input s
        if select == "s":
            ending_type = shop(player_state, current_airport_info, shop_param)
            if ending_type == 0:
                continue
            else:
                return ending_type, {}

        selected_airport = {}
        is_valid_icao = False
        for airport_info in airport_avail_list:
            if select == airport_info['ident']:
                is_valid_icao = True
                selected_airport = airport_info
                break  # break for-loop when icao is valid and continue

        # check is icao valid, if not, go back to while-loop
        if not is_valid_icao:
            print("Not a valid destination, try again")
            input("(press Enter to continue)")
        else:
            player_state["time"] -= selected_airport["time"]
            player_state["fuel"] -= selected_airport["fuel_consumption"]
            player_state["emission"] += selected_airport["emission"]
            player_state["money"] += selected_airport["reward"]
            mark_visit_airport(connection, selected_airport)

            play_flying(dest_name=selected_airport["name"],
                        dest_country=selected_airport['country_name'],
                        fuel_consumption=selected_airport["fuel_consumption"],
                        emission=selected_airport["emission"],
                        time_used=selected_airport["time"],
                        player_state=player_state,
                        reward=selected_airport["reward"])
            return 0, selected_airport


# ---------------------
# MAIN GAME
# ---------------------


def game(connection, resume=False, debug=False):
    # ---------------------
    # CONFIG
    # ---------------------

    # plane
    # fuel consumption: kg/km,
    # speed: km/h,
    # emission: g/km
    # reward: euro/km

    plane_param = {"fuel_consumption": 2,
                   "speed": 800,
                   "emission": 100,
                   "reward": 10}

    before_shop_param = {"dice_game_cost": 20,
                         "dice_bonus_percent": 1,

                         "fuel_base_percent": 5,
                         "fuel_bonus_percent": 1,

                         "treasure_value": 8000,
                         "detector_base_per_thousand": 5,
                         "detector_bonus_per_thousand": 0.5,

                         "dividend": 500}
    # every [dividend] km, add percentage to [fuel_back_percent]/[dice_bonus_percent]
    # for example: every 500km, increase 1 percentage to fuel back and dice bonus.

    shop_param = {"fuel_price": 20,
                  "win_money": 10000}

    score_param = {"money": 1,
                   "emission": 1,
                   "time": 0.01}

    # days in game
    time_limit_days = 20
    init_money = 1000
    init_fuel = 10000

    # ---------------------
    # GAME INIT (NEW GAME OR CONTINUE GAME)
    # ---------------------

    # new game or resume
    if not resume:
        # new game
        # input player name
        print("\nHello, what's your name?")
        player_name = input("> ")
        time_limit = time_limit_days * 24 * 3600
        #
        current_airport_info = generate_random_airports(connection, 25)
        player_state = {"name": player_name, "money": init_money, "fuel": init_fuel, "emission": 0,
                        "location": current_airport_info["ident"], "probability": 5, "time": time_limit, "treasure": 0,
                        "reminder": 0, "score": 0, "finish": 0}
        init_player_state(connection, player_state)
    else:
        # resume, load from database
        # check is there resume
        sql_query = "SELECT screen_name, location, finish FROM game WHERE id=(SELECT MAX(id) FROM game)"
        sql_fetch = database_execute(connection, sql_query)
        is_finish = sql_fetch[0]["finish"]
        screen_name = sql_fetch[0]["screen_name"]
        if is_finish == 0:
            print(f"You have a game save whose name is {screen_name}, do you want to continue? (Y/n)")
            select = input("> ")
            if select == "y" or select == "Y" or select == "":
                print("Game loaded, good luck!")
                player_state = load_player_state(connection, screen_name)
                player_state["name"] = screen_name
                sql_query = "SELECT name, country_name, visit FROM game_airport WHERE ident=%s"
                current_airport_info = database_execute(connection, sql_query, (player_state["location"],))[0]
                # reset last travel distance to 0, because we don't know that from game save
                current_airport_info["distance"] = 0
            else:
                print("Returning to main menu.")
                input("(press Enter to continue)")
                return 0
        else:
            print("Game save not found, returning to main menu")
            input("(press Enter to continue)")
            return 1

    # ---------------------
    # GAME START
    # ---------------------

    while True:
        # first step: go to shop
        end_type = shop(
            player_state=player_state,
            current_airport_info=current_airport_info,
            shop_param=shop_param)

        # save game in between, and check is game over
        save_player_state(connection, player_state)
        if end_type != 0:
            end_game(end_type)
            break

        # second step: departure to next airport.
        end_type, current_airport_info = departure(
            connection=connection,
            current_airport_info=current_airport_info,
            shop_param=shop_param,
            plane_param=plane_param,
            player_state=player_state)

        # save game in between, and check is game over
        save_player_state(connection, player_state)
        if end_type != 0:
            end_game(end_type)
            break

        # third step: arrive new airport
        arrive(
            current_airport_info=current_airport_info,
            plane_param=plane_param,
            before_shop_param=before_shop_param,
            player_state=player_state)

        # save game in between, (but no game over check here because game can't be over here)
        save_player_state(connection, player_state)

        # loop back to beginning

    # ---------------------
    # GAME END
    # ---------------------

    # out of loop game ended

    # high score
    last_high_score = get_highest_score(connection)
    score_dict, score = calculate_score(player_state, score_param)

    # save score and player finished game to database
    player_state["finish"] = 1
    player_state["score"] = score
    save_player_state(connection, player_state)

    # play ending score animation
    if last_high_score < score:
        is_high_score = True
    else:
        is_high_score = False
    play_score(player_state, shop_param["fuel_price"], score_dict, is_high_score)


# ---------------------
# BEFORE GAME MENU
# ---------------------
def main():
    # notify user to adjust or change to terminal
    notify_experience()

    # init database connection
    connection = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        database="flight_game",
        user="root",
        password="metro",
        autocommit=True)

    # Give player option to read story or not
    clear_screen()
    while True:
        story = input("Do you want to read background story of this game? (Y/n): ").upper()
        if story == 'N':
            break
        elif story == 'Y' or story == '':  # make Y a default option
            for line in get_story():
                print(line)
            break
        else:
            print("Invalid option! Please enter only 'y' or 'n'")
    print("\n")
    print("-------------------------------------------------------------------------------")
    print("All right! Now let's get starting your journey")
    print("-------------------------------------------------------------------------------")

    while True:
        print("1.New Game\n2.Continue\n3.High Score\n4.Exit")
        select = input("> ")
        if select == "1":
            game(connection)
        elif select == "2":
            game(connection, True)
        elif select == "3":
            print_high_score(connection)
        elif select == "4":
            break
        else:
            print("Invalid option!")


# note: end type 1: win. 2: time, 3: fuel and money, 4: coffee
if __name__ == "__main__":
    main()
