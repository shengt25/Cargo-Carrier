from flask import Flask, request, redirect, render_template
import hashlib
import time
from Game import Game
from datetime import datetime
from utils import Database
from gevent import pywsgi

# local = True
local = False

game_list = {}
airport_number = 30
database_param = {"host": "127.0.0.1",
                  "user": "root",
                  "password": "pwd",
                  "database": "cargo_carrier",
                  "port": 3306}

shop_param = {"fuel": {"price": 1, "description": "Fuel"},
              "coffee": {"price": 2, "description": "Coffee"},
              "airport": {"price": 20000, "description": "Airport"}}

player_param = {"money": 2000,
                "fuel": 1000,
                "time": 240}

plane_param = {"fuel_per_km": 1.2,
               "speed_per_h": 800,
               "emission_per_km": 0.1,
               "reward_per_km": 3,
               "hire_cost": 600}

master_database = Database(database_param)

app = Flask(__name__)


def generate_game_id():
    timestamp = str(time.time())
    hash_obj = hashlib.sha256(timestamp.encode())
    hash_string = hash_obj.hexdigest()
    game_id = hash_string[:40]
    return game_id


def print_log(game_id, text):
    # todo log response automatically with extra text and ok or fail info, etc
    current_time = datetime.now()
    formatted_text = current_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:23] + " | " + game_id + " | " + text
    print(formatted_text)


@app.route("/")
def frontpage():
    return render_template('frontpage.html')


@app.route('/highscores')
def highscores():
    return render_template('highscores.html')


@app.route('/credits')
def credits_():
    return render_template('credits.html')


@app.route("/game/<game_id>")
def game(game_id):
    if game_id not in game_list:
        print_log(game_id, "[fail] game: game not found")
        webpage = "<h1>Invalid Game Session: not found</h1>"
    else:
        is_finish = game_list[game_id].player.finish
        if is_finish:
            del game_list[game_id]
            print_log(game_id, "[fail] game: game already finished")
            webpage = "<h1>Invalid Game Session: already finished</h1>"
        else:
            print_log(game_id, "[ok] game: game home page")
            webpage = render_template('game.html')
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
        # todo not a good way to delete game session
        is_finish = game_list[game_id].player.finish
        if is_finish:
            del game_list[game_id]
            print_log(game_id, "[fail] game: game already finished")
            webpage = "<h1>Invalid Game Session: already finished</h1>"
            return webpage
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


@app.route("/game/<game_id>/check-ending")
def check_ending(game_id):
    if game_id not in game_list:
        message = "[fail] check-ending: game not found"
        print_log(game_id, message)
        response = {"success": False,
                    "message": message}
        return response

    time_ending, message = game_list[game_id].plane.check_time_ending()
    money_ending, message = game_list[game_id].plane.check_money_ending()
    print_log(game_id, message)
    score = game_list[game_id].calculate_score()
    sql_query = "UPDATE game SET score=%s WHERE game_id=%s"
    parameter = (score, game_id)

    # check time ending first because it ends the game immediately
    if time_ending:
        response = {"end": True,
                    "type": "time",
                    "score": score,
                    "message": message}
        game_list[game_id].database.query(sql_query, parameter)
        # finish the game for time ending
        return response
    if money_ending:
        response = {"end": True,
                    "type": "money",
                    "score": score,
                    "message": message}
        game_list[game_id].database.query(sql_query, parameter)
        # finish the game for money ending
        return response
    return {"end": False, "score": score, "message": message}


@app.route("/get-highscore")
def get_highscore():
    scores = []
    sql_query = "SELECT screen_name, money, fuel, emission, time, score FROM game ORDER BY score DESC LIMIT 100"
    high_scores = master_database.query(sql_query)
    for item in high_scores:
        scores.append(item["score"])
    scores.sort(reverse=True)
    for item in high_scores:
        for i, score in enumerate(scores):
            if item["score"] == score:
                item["rank"] = i + 1
                break
    return high_scores


if __name__ == "__main__":
    if local:
        app.run(debug=True, host="127.0.0.1", port=5000)
    else:
        http_server = pywsgi.WSGIServer(('0.0.0.0', 443), app,
                                        keyfile="/etc/letsencrypt/live/st17.fyi/privkey.pem",
                                        certfile="/etc/letsencrypt/live/st17.fyi/fullchain.pem")
        http_server.serve_forever()