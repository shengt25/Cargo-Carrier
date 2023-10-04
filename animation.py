import time
import os
import random


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def make_dice(num):
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


def roll_dice():
    interval = 0.05
    count = 0
    num = random.randint(1, 6)
    while count < 1.5:
        num_animation = random.randint(1, 6)
        print(make_dice(num_animation))
        time.sleep(interval)
        clear_screen()
        count += interval
    clear_screen()
    print(make_dice(num))
    return num


def plane_flying(start_name, dest_name, distance):
    length = 60
    eta = 1
    frame_rate = 60
    interval = 1 / frame_rate
    plane_icon = "🛫"

    speed = length / eta / frame_rate
    distance_per_frame = distance / eta / frame_rate

    frame_count = 0
    traveled_distance = 0
    while frame_count <= frame_rate * eta:
        pre = int(frame_count * speed)
        frame_plane = " " * (pre + len(start_name)) + plane_icon
        distance_mark = f"-- {distance}km -->"
        frame_cities = start_name + " " * int((length - len(distance_mark)) / 2) + distance_mark + " " * int(
            (length - len(distance_mark)) / 2) + dest_name
        traveled_distance += distance_per_frame
        frame_count += 1
        time.sleep(interval)
        clear_screen()

        print(frame_plane)
        print(frame_cities)


def ending_flying():
    pass