from flask import Flask, request, redirect, render_template
import hashlib
import time
from Game import Game

app = Flask(__name__)


class GameManager:
    game_list = {}


def generate_game_id():
    timestamp = str(time.time())
    hash_obj = hashlib.sha256(timestamp.encode())
    hash_string = hash_obj.hexdigest()
    temp_id = hash_string[:40]
    return temp_id


@app.route("/game/new", methods=['GET'])
def new_game():
    game_id = generate_game_id()
    print(f"{game_id}: New game")
    game_manager.game_list[game_id] = Game(game_id, database_config, item_list)

    game_manager.game_list[game_id].airport_manager.gen_airports(10)
    return redirect(f"/game/{game_id}")


@app.route("/game/<game_id>", methods=['GET'])
def game(game_id):
    if game_id not in game_manager.game_list:
        print(f"{game_id}: Game not found")
        webpage = "<h1>Game not found</h1>"
        return webpage

    webpage = "<h1>Welcome to the game</h1>" + "<br>" + f"game_id: {game_id}"  # TODO fake response
    return webpage


@app.route("/game/<game_id>/fetchAll", methods=['GET'])
def fetch(game_id):
    if game_id not in game_manager.game_list:
        print(f"{game_id}: Game not found")
        return {"success": False, "message": "Game not found"}

    print(f"{game_id}: Fetch game data")
    response_player = game_manager.game_list[game_id].player.get_state()
    response_airports = game_manager.game_list[game_id].airport_manager.get_airports()
    response = {"player": response_player, "airports": response_airports}
    return response


@app.route("/game/<game_id>/buy", methods=['POST'])
def buy(game_id):
    if game_id not in game_manager.game_list:
        print(f"{game_id}: Game not found")
        return {"success": False, "message": "Game not found"}

    data = request.get_json()
    print(f"{game_id}: buy {data}")
    return {"success": True, "money": 100, "fuel": 100}  # TODO fake response


@app.route("/game/<game_id>/fetchAirports", methods=['GET'])
def airports(game_id):
    if game_id not in game_manager.game_list:
        print(f"{game_id}: Game not found")
        return {"success": False, "message": "Game not found"}

    print(f"{game_id}: Fetch game data")
    response = game_manager.game_list[game_id].plane.get_airports_accessibility()
    return response


@app.route("/game/<game_id>/fly", methods=['POST'])
def fly(game_id):
    if game_id not in game_manager.game_list:
        print(f"{game_id}: Game not found")
        return {"success": False, "message": "Game not found"}

    data = request.get_json()
    print(f"{game_id}: fly {data}")
    return {"success": True, "money": 100, "fuel": 100, "emission": 100, "time": 100,
            "location": "BBBB"}  # TODO fake response


if __name__ == '__main__':
    database_config = {"host": "127.0.0.1",
                       "user": "root",
                       "password": "metro",
                       "database": "cargo_carrier",
                       "port": 3306}

    item_list = {"fuel": {"price": 100, "description": "Fuel"},
                 "coffee": {"price": 1, "description": "Coffee"},
                 "airport": {"price": 1000, "description": "Airport"}}
    game_manager = GameManager()
    app.run(debug=True, host="127.0.0.1", port=5000)
