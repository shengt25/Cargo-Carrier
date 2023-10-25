import os
from utils import database_execute
from utils import second_to_dhm, second_to_hm


def clear_screen():
    """Clear previous text on screen to make it tidy. NOTE: Please use terminal, because it may not work in IDE."""
    os.system("cls" if os.name == "nt" else "clear")


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
    print(f"{'   HIGH SCORE   ':{a}{len(header)}}")
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


def print_experience_notification():
    notify_env = False
    notify_width = False

    try:
        terminal_width = os.get_terminal_size()[0]
        if terminal_width < 120:
            notify_width = True
    except:
        notify_env = True

    if notify_env or notify_width:
        if notify_env:
            print("For a better experience, please use terminal/cmd(command line prompt) to run this game, thank you!")
        if notify_width:
            print("For a better experience, please adjust your window width wider than 120, thank you!")
        input("(press Enter to continue)")


def print_goal_reminder(player_state: dict):
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


def format_player_state(player_state: dict) -> str:
    """Returns the player info in formatted string (ready for print). Can be used as header in other info print."""
    a = "^"  # align to center
    w1 = 12  # align width small
    w2 = 15  # align width medium
    w3 = 20  # align width big
    money = player_state['money']
    fuel = player_state['fuel']
    emission = player_state['emission']
    location = player_state['location']
    if player_state["treasure"] == 1:
        probability = "N/A"
    else:
        # divided by 100, to convert num/10000 to num/100
        probability = str(player_state['probability'] / 100) + "%"
    dd, hh, mm = second_to_dhm(player_state['time'])
    time_left = f"{dd}d {hh}h {mm}m"
    info1 = f"{'Time Left':{a}{w1}} | {'Money':{a}{w1}} | {'Fuel':{a}{w1}} | {'CO2 Emission':{a}{w2}} | {'Location':{a}{w2}} | {'Treasure Detector':{a}{w3}}"
    info2 = f"{time_left:{a}{w1}} | {money:{a}{w1}} | {fuel:{a}{w1}} | {emission:{a}{w2}} | {location:{a}{w2}} | {probability:{a}{w3}}"
    split = "-" * len(info1)
    return "\n".join([split, info1, info2, split])


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
