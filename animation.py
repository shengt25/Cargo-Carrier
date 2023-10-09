import time
import os
import random
import copy


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


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
    info1 = f"{'Time Left':{a}{w1}} | {'Money':{a}{w1}} | {'Fuel':{a}{w1}} | {'CO2 Emission':{a}{w2}} | {'Location':{a}{w2}} | {'Detector':{a}{w1}}"
    info2 = f"{time_left:{a}{w1}} | {money:{a}{w1}} | {fuel:{a}{w1}} | {emission:{a}{w2}} | {location:{a}{w2}} | {probability:{a}{w1}}"
    split = "-" * len(info1)
    return "\n".join([split, info1, info2, split])


def make_ascii_dice(num):
    # the 1,2,3 below is placeholder, which will be replaced by "empty", "middle" and such, to make pattern.
    base_dice = """
               .-------.
              /       /| 
             /_______/ | 
             |1| |
             |2| / 
             |3|/ 
             '-------'
     """
    empty = "       "
    middle = "   o   "
    left = " o     "
    right = "     o "
    both = " o   o "
    line_1 = both
    line_2 = both
    line_3 = both

    if num == 1:
        line_1 = empty
        line_2 = middle
        line_3 = empty
    elif num == 2:
        line_1 = right
        line_2 = empty
        line_3 = left
    elif num == 3:
        line_1 = right
        line_2 = middle
        line_3 = left
    elif num == 4:
        line_2 = empty
    elif num == 5:
        line_2 = middle
    elif num == 6:
        pass
    else:
        raise Exception("Error, dice pattern not defined")
    dice = base_dice.replace("1", line_1).replace("2", line_2).replace("3", line_3)
    return dice


def play_rolling_dice(player_state, result: int):
    interval = 0.05
    length = 1
    while length > 0:
        clear_screen()
        num_animation = random.randint(1, 6)
        print(format_player_state(player_state))
        print(make_ascii_dice(num_animation))
        length -= interval
        time.sleep(interval)
    clear_screen()
    print(format_player_state(player_state))
    print(make_ascii_dice(result))

    frame = 0
    while frame <= 2:
        clear_screen()
        print(format_player_state(player_state))
        print(make_ascii_dice(result))
        print(f"It is {result}, let's see" + "." * frame)
        frame += 1
        time.sleep(0.6)


def play_detector(player_state: dict, probability_up: int, found: bool):
    detector_frame = """
                *
                |_
                (O)
                |#|
                '-'    
    """
    frame = 0
    player_state_ani = copy.deepcopy(player_state)
    player_state_ani["probability"] -= probability_up
    if probability_up > 0:
        while frame <= 3:
            clear_screen()
            print(format_player_state(player_state_ani))
            print(f"New airport, detector accuracy + {probability_up / 100}%, calibrating" + "." * frame)
            frame += 1
            time.sleep(0.6)

    player_state_ani["probability"] += probability_up
    frame = 0
    while frame <= 3:
        clear_screen()
        print(format_player_state(player_state_ani))
        print("Detecting" + "." * frame)
        print(detector_frame.replace("*", "*" + " )" * frame))
        frame += 1
        time.sleep(0.8)
    if found:
        clear_screen()
        print(format_player_state(player_state_ani))
        print("Detecting... " + "YOU FOUNT IT!!!")
        print(detector_frame.replace("*", "* !!!"))
        time.sleep(1)
    else:
        clear_screen()
        print(format_player_state(player_state_ani))
        print("Detecting..." + " no luck...")
        print(detector_frame.replace("*", ""))
        time.sleep(1)


def play_flying(dest_name, dest_country, emission, fuel_consumption, reward, time_used, player_state):
    # time of flying animation is fixed time.
    ani_length = 60
    flying_time = 2  # time of playing animation (in second)

    frame_rate = 30
    interval = 1 / frame_rate

    plane_icon = "🛫"
    frame_cloud_1 = "       ☁️                                ☁️                        ☁️"
    frame_cloud_2 = "                    ☁️                     ️                                ☁️"
    frame_cloud_3 = "          ☁️                 ☁️                 ☁️                ☁️"

    ani_speed = ani_length / flying_time / frame_rate  # character change per frame
    time_speed = time_used / flying_time / frame_rate  # time change per frame
    fuel_speed = fuel_consumption / flying_time / frame_rate  # fuel change per frame
    emission_speed = emission / flying_time / frame_rate  # emission change per frame
    reward_speed = reward / flying_time / frame_rate  # money change per frame

    frame_count = 0
    traveled_distance = 0

    # IMPORTANT, make a copy player_state for animation, other it will modify the original player_state!!!
    player_state_ani = copy.deepcopy(player_state)
    player_state_ani["fuel"] += fuel_consumption
    player_state_ani["time"] += time_used
    player_state_ani["emission"] -= emission
    player_state_ani["money"] -= reward

    while frame_count <= frame_rate * flying_time:
        cloud_move_1 = int(frame_count / 5)
        cloud_move_2 = int(frame_count / 10)
        cloud_move_3 = int(frame_count / 20)

        clear_screen()

        pre = int(frame_count * ani_speed)
        frame_plane = " " * pre + plane_icon
        frame_city = f"DST: {dest_name} ({dest_country})"
        traveled_distance += ani_speed
        frame_count += 1
        player_state_ani["fuel"] = round(player_state_ani["fuel"] - fuel_speed)
        player_state_ani["time"] = round(player_state_ani["time"] - time_speed)
        player_state_ani["emission"] = round(player_state_ani["emission"] + emission_speed)
        player_state_ani["money"] = round(player_state_ani["money"] + reward_speed)
        print(format_player_state(player_state_ani))
        print(frame_city)
        print(frame_plane)
        print("\n")
        print(frame_cloud_1[cloud_move_1:])
        print(frame_cloud_2[cloud_move_2:])
        print(frame_cloud_3[cloud_move_3:])
        print("\n")
        time.sleep(interval)


def play_coffee_ending():
    coffee_steam = ["              )  (",
                    "         (   ) )",
                    "          ) ( ("]
    coffee_frame = """        _______)_
     .-'---------|  
    ( C|         |
     '-.         |
       '_________'
        '-------'    
    """
    message = ("You drank too much coffee all at once, and don't feel good.\n"
               "Doctor came and told you:\n"
               "Sorry but you have to stay at hospital for at least a month.\n"
               "Unfortunately, this is the end of your journey.\n")
    for i in range(0, 4):
        clear_screen()
        print("\n" * (3 - i))
        for j in range(3 - i, 3):
            print(coffee_steam[j])
        print(coffee_frame)
        print(message)
        time.sleep(0.8)
    input("(press Enter to continue)")


def play_time_ending():
    clock_frame_1 = r"""
        _..--.._ 
      .' .  0 . '.\
     / .        .  \
    ; .          . |;
    |45    () ___15||
    ; .          . |;
     \\ .        . /
      \'___'30'___'
    """
    clock_frame_2 = r"""
        _..--.._ 
      .' .  0 . '.\
     / .      / .  \
    ; .      /   . |;
    |45    ()    15||
    ; .          . |;
     \\ .        . /
      \'___'30'___'
      """
    clock_frame_3 = r"""
        _..--.._ 
      .' .  0 . '.\
     / .    |   .  \
    ; .     |    . |;
    |45    ()    15||
    ; .          . |;
     \\ .        . /
      \'___'30'___'
      """
    clear_screen()
    print(clock_frame_1)
    time.sleep(1)
    clear_screen()
    print(clock_frame_2)
    time.sleep(1)
    clear_screen()
    print(clock_frame_3)
    time.sleep(1)
    print("Time runs out... And you didn't earn enough money")
    input("(press Enter to continue)")


def play_money_ending():
    money_frame = r"""
             _____
          .-'     `-. 
        .'  .-''''-.-'
       /  .'
  .---' '--------.
   ''':  :'''''''
.-----'  '-----.
 '''''\  \''''''
       \  `.
        '.  `-----.
          '-.____.' 
    """
    count = len(money_frame)
    clear_screen()
    print(money_frame)
    time.sleep(1.5)
    for i in range(11):
        clear_screen()
        print(money_frame[int(i * count / 10):])
        time.sleep(0.1)
    print("You don't have any money or fuel to go anywhere.")
    input("(press Enter to continue)")


def play_win():
    fireworks = [r"                                   .''.",
                 r"       .''.      .        *''*    :_\/_:     .",
                 r"      :_\/_:   _\(/_  .:.*_\/_*   : /\ :  .'.:.'.",
                 r"  .''.: /\ :   ./)\   ':'* /\ * :  '..'.  -=:o:=-",
                 r" :_\/_:'.:::.    ' *''*    * '.\'/.' _\(/_'.':'.'",
                 r" : /\ : :::::     *_\/_*     -= o =-  /)\    '  *",
                 r"  '..'  ':::'     * /\ *     .'/.\'.   '",
                 r"      *            *..*         :",
                 r"        *",
                 r"        *"]
    for i in range(0, 11):
        clear_screen()
        print("\n" * (10 - i))
        for j in range(10 - i, 10):
            print(fireworks[j])
        time.sleep(0.2)
    print("CONGRATULATIONS!!! You just opened your own airport! Tiny, but lovely!")
    print("Finally, your dream came true!")
    input("(press Enter to continue)")
    play_credit()


def play_credit():
    credits_list = ["",
                    "",
                    "Director",
                    "Vitalii Virronen",
                    "",
                    "Document",
                    "Thien Luu",
                    "",
                    "Game Designer",
                    "Thien Luu",
                    "Loc Dang",
                    "Vitalii Virronen",
                    "Sheng Tai",
                    "",
                    "Lead Programmer",
                    "Sheng Tai",
                    "Loc Dang",
                    "",
                    "Programmer",
                    "Vitalii Virronen",
                    "Thien Luu",
                    "",
                    "Graphic and Animation",
                    "Sheng Tai",
                    "",
                    "Story",
                    "Vitalii Virronen",
                    "",
                    "Testing",
                    "Loc Dang",
                    "Sheng Tai",
                    "",
                    "",
                    "",
                    "",
                    "Thank you for playing!"
                    ]
    for credits in credits_list:
        print(f"{credits:^50}")
        time.sleep(0.4)
    input("(press Enter to continue)")


def play_score(player_state: dict, fuel_price, score_dict, is_high_score: bool):
    score = score_dict["money"] + score_dict["time"] - score_dict["emission"]

    player_state_ani = copy.deepcopy(player_state)
    play_time = 0.8
    pause_time = 0.8
    frame_rate = 30
    interval = 1 / frame_rate

    line_score_name = ""
    line_score = ""

    # animation list
    animation_names = ["time", "money", "emission"]

    if player_state_ani["fuel"] > 0:
        fuel_step = int(player_state_ani["fuel"] / play_time / frame_rate)
        fuel_to_money = player_state_ani["fuel"] * fuel_price
        fuel_to_money_step = int(fuel_to_money / play_time / frame_rate)
        while True:
            clear_screen()
            print(format_player_state(player_state_ani))
            if player_state_ani["fuel"] > 0 and fuel_step >= 1 and fuel_to_money_step >= 1:
                player_state_ani["fuel"] -= fuel_step
                player_state_ani["money"] += fuel_to_money_step
            else:
                player_state_ani["fuel"] = 0
                clear_screen()
                print(format_player_state(player_state_ani))
                print(line_score_name)
                print(line_score)
                break
            time.sleep(interval)
        time.sleep(pause_time)

    for animation_name in animation_names:
        time_step = int(player_state_ani[animation_name] / play_time / frame_rate)
        while True:
            clear_screen()
            print(format_player_state(player_state_ani))
            print(line_score_name)
            print(line_score)
            # when value > 0, change and continue next loop.
            if player_state_ani[animation_name] > 0 and time_step >= 1:
                player_state_ani[animation_name] -= time_step
            # when value = 0, go to next animation.
            else:
                player_state_ani[animation_name] = 0
                clear_screen()
                print(format_player_state(player_state_ani))
                print(line_score_name)
                print(line_score)
                break
            time.sleep(interval)
        if animation_name == "time":
            split = ""
        elif animation_name == "emission":
            split = "\t-\t"
        else:
            split = "\t+\t"
        line_score_name += split + animation_name
        line_score += split + str(score_dict[animation_name])
        time.sleep(pause_time)

    for i in range(2):
        clear_screen()
        print(format_player_state(player_state_ani))
        if i == 0:
            print(line_score_name)
            print(line_score)
        else:
            print(line_score_name + "\tscore")
            print(line_score + f"\t=\t{score}")
        time.sleep(pause_time)

    if is_high_score:
        print("\nNEW HIGH SCORE!\n")
    input("(press Enter to continue)")


def play_intro():
    pass


# test
def test():
    player_state_ani = {"name": "test", "money": 10, "fuel": 100, "emission": 100, "location": "LKPR",
                        "probability": 5, "time": 500, "treasure": 0}

    shop_param = {"fuel_price": 20,
                  "win_money": 10000}

    score_param = {"money": 1,
                   "emission": 1,
                   "time": 1}
    # play_flying(dest_name="Cagliari Elmas Airport",
    #             dest_country="Italy",
    #             fuel_consumption=3000,
    #             time_used=10000,
    #             player_state=player_state_ani)

    score_dict = {"money": 100, "time": 200, "emission": 300, "total": 300}
    # play_detector(player_state_ani, 4, True)
    # play_rolling_dice(player_state_ani,5)
    # play_coffee_ending()
    # play_time_ending()
    # play_money_ending()
    # play_win()
    # play_credit()
    play_score(player_state_ani, 20, score_dict, True)


if __name__ == "__main__":
    test()
