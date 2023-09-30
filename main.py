import threading, queue
import os
import time

MENU_FREEZE = 0
MENU_NORMAL = 1
VALUE_MONEY = 2
VALUE_FUEL = 3
VALUE_EMISSION = 4
DEFREEZE = -1


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def decode_message(queue_item: list):
    command = queue_item[0]
    content = ""
    try:
        for item in queue_item[1:]:
            content += item + "\n"
    except:
        pass
    return command, content


def get_message(q):
    if q.qsize() != 0:
        return q.get()
    # messages = []
    # for _ in range(q.qsize()):
    #     messages.append(q.get())
    #     # or process message here
    # return messages


def game_front(q):
    game_time = 100
    print_plus = ""
    money = 0
    fuel = 0
    emission = 0
    pause_flag = False
    pause_text = ""
    while True:
        message_new = get_message(q)
        if message_new is not None:
            message_type, message_content = decode_message(message_new)
            if message_type == MENU_NORMAL:
                print_plus = message_content
            elif message_type == MENU_FREEZE:
                print_plus = message_content
                pause_flag = True
                pause_text = "(Pause)"

        print_whole = (f"Player: A, time left: {game_time}{pause_text}\n"
                       f"Money: {money}\n"
                       f"Fuel: {fuel}\n"
                       f"Emission: {emission}\n"
                       f"------------------\n") + print_plus

        if pause_flag == False:
            print(print_whole)
        else:
            print(print_whole)
            q.get()  # use queue to block the thread
            pause_flag = False
            pause_text = ""

        game_time -= 1
        time.sleep(1)
        cls()


def game_back(q):
    while True:
        q.put([MENU_NORMAL, "Menu", "1: buy", "2: upgrade"])
        while True:
            key = input()
            if key == "1":
                q.put([MENU_NORMAL, "Hi, what can I do for you?", "1: buy fuel", "2: buy emission", "3: exit"])
                while True:
                    key = input()
                    if key == "1":
                        q.put([MENU_FREEZE, "How many litres fuel?"])
                        key = input()
                        q.put(DEFREEZE)
                    if key == "2":
                        q.put([MENU_FREEZE, "How many litres co2?"])
                    if key == "3":
                        q.put([MENU_NORMAL, "Menu", "1: buy", "2: upgrade"])
                        break

            elif key == "2":
                q.put([MENU_NORMAL, "Ok, which plane would you like to upgrade?"])
                key = input()

            if key == "1":
                q.put([MENU_FREEZE])
                key = input()


if __name__ == "__main__":
    q = queue.Queue()
    thread_game = threading.Thread(target=game_front, args=(q,))
    thread_game.start()

    thread_display = threading.Thread(target=game_back, args=(q,))
    thread_display.start()

    # thread_timer = threading.Thread(target=timer, args=())
    # thread_show = threading.Thread(target=show, args=())
    #
    # thread_timer.start()
    # thread_show.start()
    #
    # thread_timer.join()
    # thread_show.join()
