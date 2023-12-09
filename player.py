from utils import database_execute


# ---------------------
# PLAYER STATE
# ---------------------

def save_player_state(connection, player_state: dict) -> None:
    """
    Save player state to database. (money, fuel, emission, location, probability, time)
    :param connection: SQL connection
    :param player_state: Player state dictionary
    """
    # sql_query_old = ("UPDATE game SET money=%s, fuel=%s, emission=%s, location=%s, probability=%s, "
    #                  "treasure=%s, time=%s, score=%s, finish=%s WHERE screen_name=%s "
    #                  "AND id=(SELECT MAX(id) from game WHERE screen_name=%s)")
    # if using mysql, need to change the query like this below
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
