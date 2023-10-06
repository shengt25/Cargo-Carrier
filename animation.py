import time
import os
import random


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def make_ascii_dice(num):
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
        line_1 = both
        line_2 = empty
        line_3 = both
    elif num == 5:
        line_1 = both
        line_2 = middle
        line_3 = both
    elif num == 6:
        line_1 = both
        line_2 = both
        line_3 = both
    else:
        print("Error, not defined")
        return 1
    dice = base_dice.replace("1", line_1).replace("2", line_2).replace("3", line_3)
    return dice


def play_rolling_dice(result: int):
    interval = 0.05
    length = 1
    while length > 0:
        clear_screen()
        num_animation = random.randint(1, 6)
        print(make_ascii_dice(num_animation))
        length -= interval
        time.sleep(interval)
    clear_screen()
    print(make_ascii_dice(result))

    frame = 0
    while frame <= 4:
        clear_screen()
        print(make_ascii_dice(result))
        print(f"The result is {result}, let's see" + "." * frame)
        frame += 1
        time.sleep(0.8)

def play_flying(start_name, dest_name, distance, player_state_formatted):
    speed = 800
    ani_length = 60
    time_scale = 1800

    eta_game = (distance / speed) * 60  # time in game (minutes)
    eta_real = eta_game * 60 / time_scale  # time in real world (second)

    frame_rate = 60
    interval = 1 / frame_rate
    plane_icon = "🛫"

    ani_speed = ani_length / eta_real / frame_rate  # block speed per frame

    frame_count = 0
    traveled_distance = 0
    while frame_count <= frame_rate * eta_real:
        clear_screen()

        pre = int(frame_count * speed)
        frame_plane = " " * (pre + len(start_name)) + plane_icon
        distance_mark = f"-- {distance}km -->"
        frame_cities = start_name + " " * int((ani_length - len(distance_mark)) / 2) + distance_mark + " " * int(
            (ani_length - len(distance_mark)) / 2) + dest_name
        traveled_distance += ani_speed
        frame_count += 1

        print(player_state_formatted)
        print(frame_plane)
        print(frame_cities)
        time.sleep(interval)
