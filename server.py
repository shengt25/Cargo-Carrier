from flask import Flask, request, redirect, render_template
import hashlib
import time
from Game import Game
from datetime import datetime

app = Flask(__name__)
game_list = {}
airport_number = 10
database_param = {"host": "127.0.0.1",
                  "user": "root",
                  "password": "metro",
                  "database": "cargo_carrier",
                  "port": 3306}

shop_param = {"fuel": {"price": 100, "description": "Fuel"},
              "coffee": {"price": 1, "description": "Coffee"},
              "airport": {"price": 1000, "description": "Airport"}}

player_param = {"money": 100000,
                "fuel": 100000,
                "time": 800}

plane_param = {"fuel_per_km": 0.1,
               "speed_per_h": 1.2,
               "emission_per_km": 1.2,
               "reward_per_km": 2,
               "hire_cost": 600}


def generate_game_id():
    timestamp = str(time.time())
    hash_obj = hashlib.sha256(timestamp.encode())
    hash_string = hash_obj.hexdigest()
    game_id = hash_string[:40]
    return game_id


def print_log(game_id, text):
    current_time = datetime.now()
    formatted_text = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:23] + " | " + game_id + " | " + text
    print(formatted_text)


@app.route("/game/<game_id>")
def game(game_id):
    if game_id not in game_list:
        print_log(game_id, "[fail] game: game not found")
        webpage = "<h1>Game not found</h1>"
    else:
        print_log(game_id, "[ok] game: game home page")
        webpage = "<h1>Welcome to the game</h1>" + "<br>" + f"game_id: {game_id}"  # TODO fake response
    return webpage


@app.route("/game/<game_id>/get-all-data")
def get_all_data(game_id):
    if game_id not in game_list:
        message = "[fail] get-all-data: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "message": message}
    else:
        message = "[ok] get-all-data"
        print_log(game_id, message)
        response_player = game_list[game_id].player.get_all_data()
        response_airports = game_list[game_id].plane.get_all_airports()
        response = {"success": True,
                    "message": message,
                    "player": response_player,
                    "airports": response_airports}
    return response


@app.route("/game/<game_id>/get-airports-data")
def get_airports_data(game_id):
    if game_id not in game_list:
        message = "[fail] get-airports-data: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "message": message}
    else:
        message = "[ok] get-airports-data"
        print_log(game_id, message)
        response = {"success": True,
                    "message": message,
                    "airports": game_list[game_id].plane.get_all_airports()}
    return response


@app.route("/game/<game_id>/get-player-data")
def get_player_data(game_id):
    if game_id not in game_list:
        message = "[fail] get-player-data: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "message": message}
    else:
        message = "[ok] get-player-data"
        print_log(game_id, message)
        response = {"success": True,
                    "message": message,
                    "player": game_list[game_id].player.get_all_data()}
    return response


@app.route("/game/new-game", methods=["POST"])
def new_game():
    # get player's name
    data = request.get_json()
    player_name = data["name"]

    # generate new random game_id
    game_id = generate_game_id()

    # re-generate if game_id already exists
    while game_id in game_list:
        print_log(game_id, "[wtf] What? game_id already exists, re-generating")
        game_id = generate_game_id()

    # create new game
    message = "[ok] creating new game"
    print_log(game_id, message)
    game_list[game_id] = Game(game_id=game_id,
                              database_param=database_param,
                              player_name=player_name,
                              airport_number=airport_number,
                              shop_param=shop_param,
                              player_param=player_param,
                              plane_param=plane_param)
    response = {"success": True,
                "message": message,
                "gameID": game_id}
    return response


@app.route("/game/<game_id>/buy", methods=["POST"])
def buy(game_id):
    if game_id not in game_list:
        message = "[fail] buy: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "reason": "game",
                    "message": message}
    else:
        data = request.get_json()
        item = data["item"]
        amount = data["amount"]
        if item == "fuel":
            response = game_list[game_id].shop.buy_fuel(amount)
            print_log(game_id, response["message"])
        elif item == "airport":
            response = game_list[game_id].shop.buy_airport()
            print_log(game_id, response["message"])
        else:
            response = game_list[game_id].shop.buy_item(item, amount)

            print_log(game_id, response["message"])

    return response


@app.route("/game/<game_id>/fly", methods=["POST"])
def fly(game_id):
    if game_id not in game_list:
        message = "[fail] fly: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "message": message}
    else:
        data = request.get_json()
        response = game_list[game_id].plane.fly(ident=data["ident"])
        print_log(game_id, response["message"])
    return response


@app.route("/game/<game_id>/unload", methods=["POST"])
def unload(game_id):
    if game_id not in game_list:
        message = "[fail] unload: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "message": message}
    else:
        data = request.get_json()
        option = data["option"]
        response = game_list[game_id].plane.unload(option)
        print_log(game_id, response["message"])
    return response


if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)
