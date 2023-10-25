import random
import copy
from display import print_goal_reminder, format_player_state, format_airport_list, clear_screen
from airport import get_airports_in_range, mark_visit_airport
from animation import play_win, play_time_ending, play_money_fuel_ending, play_coffee_ending
from animation import play_rolling_dice, play_flying, play_detector


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
        play_money_fuel_ending()
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
            print_goal_reminder(player_state)
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
        select = input("> ").strip()
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
        print_goal_reminder(player_state)
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
        select = input("> ").strip()
        if select == "1":  # buy fuel
            welcome_message = "So, ready to go?"
            print(f"Okay, the price is €{shop_param['fuel_price']}/kg, how much do you want? (enter money)")
            try:
                expense = int(input("> ").strip())
            except:
                print("Hmm, please tell me only numbers.")
                input("(press Enter to continue)")
            else:
                amount = round(expense / shop_param['fuel_price'])
                print(f"With €{expense} you can buy {amount} kg fuel, is that ok?")
                print("(press Enter to continue, input c to cancel)")
                confirm = input("> ").strip()
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
        select = input("> ").strip().upper()

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
