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
    notify = False
    try:
        terminal_width = os.get_terminal_size()[0]
    except:
        terminal_width = -1
    try:
        is_idle = "idlelib" in sys.modules
    except:
        is_idle = True
    if terminal_width < 0 or is_idle:
        notify = True
        print("Please use terminal environment for a better experience, thank you!")
    if 0 < terminal_width < 120:
        notify = True
        print("Please adjust your terminal width wider than 120 for a better experience, thank you!")
    if notify:
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
            airport_info["emission"] = round(distance * plane_param["emission"])
            airport_info["reward"] = round(airport_info["distance"] * plane_param["reward"])

            # if anywhere is in range of time, set flag_no_time to False
            if distance <= range_by_time:
                flag_no_time = False
                # then check fuel range
                if distance <= range_by_fuel:
                    airports_in_range.append(airport_info)
                else:
                    airports_out_of_range.append(airport_info)
    airports_in_range.sort(key=lambda x: x["distance"])
    airports_out_of_range.sort(key=lambda x: x["distance"])
    if airport_now is None:
        raise Exception("Cannot get current airport, please restart the game.")
    return airport_now, airports_in_range, airports_out_of_range, flag_no_time


def mark_visit_airport(connection, selected_airport):
    if selected_airport["visit"] == 0:
        sql_query = "UPDATE game_airport SET visit=1 WHERE ident=%s"
        database_execute(connection, sql_query, (selected_airport["ident"],))


def format_airport_list(airport_list: list, airport_now=False) -> list:
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
                raise Exception("You are at here, but it marked not visited? Hacker!!!")
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
            output = (f"{column_name:{a}{w3}} {column_icao:{a}{w1}} {column_reward:{a}{w1}} {column_distance:{a}{w2}} "
                      f"{column_eta:{a}{w1}} {column_emission:{a}}")

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
    sql_query_old = ("UPDATE game SET money=%s, fuel=%s, emission=%s, location=%s, probability=%s, "
                     "treasure=%s, time=%s, score=%s, finish=%s WHERE screen_name=%s "
                     "AND id=(SELECT MAX(id) from game WHERE screen_name=%s)")

    # if using mysql, need to change the query like this
    # online database
    sql_query = ("UPDATE game SET money=%s, fuel=%s, emission=%s, location=%s, probability=%s, "
                 "treasure=%s, time=%s, score=%s, finish=%s WHERE screen_name=%s "
                 "AND id=(SELECT MAX(id) from (SELECT * FROM game) as game WHERE screen_name=%s)")

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
    clear_screen()
    print(format_player_state(player_state))
    print("Congratulations! You already have enough money for opening your airport!")
    print("You can choose go home airport or continue earning money (or losing money).")
    print("But be careful with time... and your money")
    print(f"Anyway, you can always make your choice.")
    print("\nTips:")
    print("You can now choose OPEN MY OWN AIRPORT at home, to finish game ")
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
    clear_screen()
    print("-" * len(header))
    print(f"{'   HIGH SCORE   ':-{a}{len(header)}}")
    print("-" * len(header))
    print(header)
    print("-" * len(header))
    for data in data_dict:
        score = data["score"]
        if score > 0:
            name = data["screen_name"]
            money = data["money"]
            fuel = data["fuel"]
            emission = data["emission"]

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
    print("\n")
    return


def calculate_score(player_state, score_param):
    score_money = round(score_param["money"] * player_state["money"])
    score_emission = round(score_param["emission"] * player_state["emission"])
    score_time = round(score_param["time"] * player_state["time"])
    score = score_money + score_time - score_emission
    player_state["score"] = score
    score_dict = {"money": score_money, "time": score_time, "emission": score_emission}
    return score_dict, score


# ---------------------
# MAIN GAME MODULE
# ---------------------

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


def arrival(current_airport_info: dict, arrival_param: dict, player_state: dict, shop_param):
    """
    Player detects treasure and play dice game here.
    :param current_airport_info:
    :param arrival_param:
    :param player_state:
    :return:
    """
    # fix update current airport ICAO
    player_state['location'] = current_airport_info['ident']

    # check is this unvisited airport
    airport_name = current_airport_info['name']
    country_name = current_airport_info['country_name']
    distance_last_fly = current_airport_info['distance']

    # set up bonus
    dice_bonus_percent = round(distance_last_fly / arrival_param["dividend"] * arrival_param["dice_bonus_percent"], 2)

    # detect treasure when it is not yet done
    if player_state["treasure"] == 0:
        probability_up = 0
        if current_airport_info['visit'] == 0:
            # set up probability, round to int, (use num ‰)
            probability_bonus = distance_last_fly / arrival_param["dividend"] * arrival_param[
                "detector_bonus_per_10k"]
            probability_up = round(arrival_param["detector_base_per_10k"] + probability_bonus)
            player_state["probability"] += probability_up

        # the probability is per 10 thousand (such as 52/10000, which equivalent to 0.52%)
        detection = random.randint(1, 10000)
        if detection <= player_state["probability"]:
            # detected
            play_detector(player_state, probability_up, True)
            print(f"You FOUND THE TREASURE and it worth €{arrival_param['treasure_value']}")
            print(f"And the detector has magically broken now.")
            input("(press Enter to continue)")
            player_state["money"] += arrival_param["treasure_value"]
            player_state["treasure"] = 1
            player_state["probability"] = -1
        else:
            # not detected
            play_detector(player_state, probability_up, False)
            input("(press Enter to continue)")
        if player_state["money"] > shop_param['win_money'] and player_state["reminder"] == 0:
            goal_reminder(player_state)
            player_state["reminder"] = 1  # welcome_message = (f"Hello and welcome to {airport_name} in {country_name}"
    #                    f"\n\nWanna unload the cargo by yourself? There's always REWARD and RISK!"
    #                    f"\nOr you can hand me over, for €{arrival_param['hand_over_cost']}! "
    #                    f"NO RISK, but also NO REWARD."
    #                    f"\n\n(reward bonus +{dice_bonus_percent}%)")
    welcome_message = (f"Hello and welcome to {airport_name} in {country_name}"
                       f"\n\nNow you need to unload the cargo, two choices: "
                       f"\nI.  Do it yourself: a dice game will decide your fate."
                       f"\nII. Hire someone  : for only €600, no risk but no reward."
                       f"\n\n(reward bonus +{dice_bonus_percent}%)")
    # change welcome message when at home
    if current_airport_info['visit'] == 2:
        welcome_message.replace("Hello, welcome to", "Welcome home, ")
    # dice game
    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)
        print("\n1. Unload by myself (dice game)\n2. Hire someone (pay €600)\n3. What dice game?")
        select = input("> ")
        if select == "1":  # go dice game
            print("Great! Tell me when you're ready.")
            input("(press Enter to continue)")
            result = random.randint(1, 6)
            play_rolling_dice(player_state, result)
            if result == 1:
                dice_message = ("Oh no! Your competitor secretly broke your precious cargo, "
                                "that cost 90% of your deposit!!! You are so angry but he ran away!")
                player_state["money"] = round(player_state["money"] * 0.1)
            elif result == 2:
                dice_message = "The cargo is heavily damaged, you lost €1500!"
                player_state["money"] -= 1500
                # when player don't have enough money.
                if player_state["money"] < 0:
                    player_state["money"] = 0
                    dice_message = (dice_message +
                                    "\nYou don't have enough money! But the insurance company paid the rest.")
            elif result == 3:
                dice_message = "Well, things go smoothly, nothing happened to you."
            elif result == 4:
                earned = 1500 + round(1500 * dice_bonus_percent / 100)
                dice_message = (f"Wow! You did a great job and earned extra €{earned} "
                                f"(with {dice_bonus_percent}% distance bonus)")
                player_state["money"] += earned
            elif result == 5:
                earned = 1800 + round(1800 * dice_bonus_percent / 100)
                dice_message = (f"Great! The owner of cargo is very happy and gave you a tips for €{earned} "
                                f"(with {dice_bonus_percent}% distance bonus)")
                player_state["money"] += earned
            else:
                multiply = 2 + round(2 * dice_bonus_percent / 100, 2)
                dice_message = (f"You are so lucky!!! Turned out it was a very special cargo "
                                f"and the owner was so happy.\n"
                                f"Your deposit just multiplied by {multiply} (with {dice_bonus_percent}% bonus)")
                player_state["money"] = round(player_state["money"] * multiply)
            print(dice_message)
            input("(press Enter to continue)")
            break

        elif select == "2":  # hand over
            if player_state["money"] <= arrival_param["hand_over_cost"]:
                print("Hmm, maybe you wanna do it yourself? Because you don't have enough M0nEy... yeah")
                input("(press Enter to continue)")
            else:
                print(f"Great, you made a wise choice! hehehe...")
                input("(press Enter to continue)")
                player_state["money"] -= arrival_param["hand_over_cost"]
                break

        elif select == "3":  # about game
            print(f"\nHello {player_state['name']}, the dice has risk and rewards:\n")
            print(f"\nDice  1: money - 90%"
                  f"\n      2: money - 1500"
                  f"\n      3: money + 0"
                  f"\n      4: money + 1500     + bonus"
                  f"\n      5: money + 1800     + bonus"
                  f"\n      6: money * 2        + bonus  (bonus = {dice_bonus_percent}% based on last travel distance)"
                  f"\n")
            print("\nNow, make you choice...")
            input("(press Enter to continue)")
        else:
            print("Sorry that is not an option.")
            input("(press Enter to continue)")
        welcome_message = (f"So, make you decision, unload yourself "
                           f"or cost €{arrival_param['hand_over_cost']} to hand me over.")


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
    welcome_message = f"Hello {player_state['name']}, welcome to my shop! What can I help you?"
    # print menu, wait for selection, until player choose to leave.
    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)

        # at home
        if current_airport_info["visit"] == 2:
            print("\n1. Buy fuel\n2. Take off\n3. Have some coffee\n4. Open my own airport")
        else:
            print("\n1. Buy fuel\n2. Take off\n3. Have some coffee")
        select = input("> ")
        if select == "1":  # buy fuel
            welcome_message = "So, ready to go?"
            print(f"Okay, the price is €{shop_param['fuel_price']}/kg, how much do you want? (enter money)")
            try:
                expense = int(input("> "))
            except:
                print("Hmm, please tell me only numbers.")
                input("(press Enter to continue)")
            else:
                amount = round(expense / shop_param['fuel_price'])
                print(f"With €{expense} you can buy {amount} kg fuel, is that ok?")
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
            if player_state["money"] < 3:
                print("Interesting, you can't even afford a cup of coffee!")
                input("(press Enter to continue)")
            else:
                player_state["money"] -= 3
                coffee_count += 1
                if coffee_count >= 10:
                    return 4  # coffee ending
                else:
                    welcome_message = "Great coffee, right? What do you need now?"
                    print("You spent €3, had a cup of coffee, feel refreshed, nothing else happened")
                    input("(press Enter to continue)")
        elif select == "4" and current_airport_info["visit"] == 2:
            if player_state["money"] < shop_param["win_money"]:
                print("Well, you don't have enough money.")
                print("\nReminder:")
                print(f"Your main goal is to earn €{shop_param['win_money']} to open your own airport.")
                print(f"But now you only have €{player_state['money']}, come back later.")
                input("(press Enter to continue)")
            else:
                return 1  # game won!

        else:  # wrong option
            welcome_message = "Anything else?"
            print("Sorry that is not an option.")
            input("(press Enter to continue)")
    return 0  # game continue


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
              f"{'ICAO':{a}{w1}} {'Reward':{a}{w1}} {'Distance (Fuel)':{a}{w2}} {'ETA':{a}{w1}} {'Emission':{a}}")
    split_header = len(header) * "-"

    split_here = "You Are Here"
    split_out = f"\n{'Out of Reach':.<{len(header)}}"
    split_available = f"\n{'Available':.<{len(header)}}"
    airport_now, airport_avail_list, airport_out_list, flag_no_time = get_airports_in_range(connection, plane_param,
                                                                                            player_state)
    airport_avail_detail_list = format_airport_list(airport_avail_list)
    airport_out_detail_list = format_airport_list(airport_out_list)
    airport_now_detail = format_airport_list([airport_now], True)[0]

    while True:
        clear_screen()
        print(format_player_state(player_state))
        print(welcome_message)
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
                    print("\n")
                    print("You don't have enough fuel, but still have some money,")
                    print("Why not going back to shop and buy some?")

        print("\nYour next destination, enter ICAO, or enter s to go back shop:")
        select = input("> ").upper()

        # go back to shop when input s
        if select == "S":
            ending_type = shop(player_state, current_airport_info, shop_param)
            # update available and out of range list after buying fuel again
            _, airport_avail_list, airport_out_list, _ = get_airports_in_range(connection, plane_param, player_state)
            airport_avail_detail_list = format_airport_list(airport_avail_list)
            airport_out_detail_list = format_airport_list(airport_out_list)
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

    plane_param = {"fuel_consumption": 1.2,
                   "speed": 800,
                   "emission": 0.1,
                   "reward": 1.2}

    arrival_param = {"hand_over_cost": 600,
                     "dice_bonus_percent": 4,

                     "treasure_value": 20000,
                     "detector_base_per_10k": 20,
                     "detector_bonus_per_10k": 50,

                     "dividend": 500}
    # every [dividend] km, add percentage to [fuel_back_percent]/[dice_bonus_percent]
    # for example: every 500km, increase 1 percentage to fuel back and dice bonus.

    shop_param = {"fuel_price": 0.8,
                  "win_money": 20000}

    score_param = {"money": 1,
                   "emission": 1,
                   "time": 0.01}

    time_limit_days = 5  # days in game
    init_money = 2000
    init_fuel = 0
    init_probability = 5
    num_of_airport = 30

    # ---------------------
    # GAME INIT (NEW GAME OR CONTINUE GAME)
    # ---------------------

    # new game or resume
    if not resume:
        # new game
        # input player name
        while True:
            print("\nHello, what's your name?")
            player_name = input("> ")
            if player_name.isspace() or player_name == "":
                print("Enter your name please.")
            else:
                break

        time_limit = time_limit_days * 24 * 3600
        #
        current_airport_info = generate_random_airports(connection, num_of_airport)
        player_state = {"name": player_name, "money": init_money, "fuel": init_fuel, "emission": 0,
                        "location": current_airport_info["ident"], "probability": init_probability, "time": time_limit,
                        "treasure": 0, "reminder": 0, "score": 0, "finish": 0}
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
                input("(press Enter to continue)")
                clear_screen()
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

        # save game in between
        save_player_state(connection, player_state)
        # check is game over
        if end_type != 0:
            end_game(end_type)
            break

        # second step: depart to next airport.
        end_type, current_airport_info = departure(
            connection=connection,
            current_airport_info=current_airport_info,
            shop_param=shop_param,
            plane_param=plane_param,
            player_state=player_state)

        # save game in between
        save_player_state(connection, player_state)
        # check is game over
        if end_type != 0:
            end_game(end_type)
            break

        # third step: arrive new airport
        arrival(
            current_airport_info=current_airport_info,
            arrival_param=arrival_param,
            player_state=player_state,
            shop_param=shop_param)

        # save game in between, (but no game over check here because game can't be over here)
        save_player_state(connection, player_state)

        # loop back to beginning

    # ---------------------
    # GAME END
    # ---------------------

    # out of loop game ended

    # high score
    if end_type == 1:
        last_high_score = get_highest_score(connection)
        score_dict, score = calculate_score(player_state, score_param)
        # set player's score when win
        player_state["score"] = score
        # play ending score animation
        if last_high_score < score:
            is_high_score = True
        else:
            is_high_score = False
        play_score(player_state, shop_param["fuel_price"], score_dict, is_high_score)
    else:
        # not win, no score
        player_state["score"] = 0
        print("Not calculating score because it's only for winner.")
        print("Try harder next time!")
        input("(press Enter to continue)")

    # set player finished game
    player_state["finish"] = 1
    # save all above to database
    save_player_state(connection, player_state)


# ---------------------
# GAME MAIN MENU
# ---------------------
def main():
    # init database connection
    use_local_database = False

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
    notify_experience()

    # Give player option to read story or not
    clear_screen()
    while True:
        story = input("Do you want to read background story of this game? (Y/n): ").upper()
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
            print("Invalid option!\n")


# note: end type 1: win. 2: time, 3: fuel and money, 4: coffee
if __name__ == "__main__":
    main()
