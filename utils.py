# ---------------------
# UTILITIES
# ---------------------


def database_execute(connection, sql_query, parameter: tuple = None) -> dict:
    """
    Execute sql command and return the result
    :param connection: SQL connection.
    :param sql_query: Sql query, replace variable with placeholder "%s"
    :param parameter: Variable in tuple. If only one then: (1, )
    :return: Dict type response
    """
    # convert to tuple if parameter a single data
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql_query, parameter)
    response = cursor.fetchall()
    return response


def second_to_hm(seconds: int) -> tuple[int, int]:
    """
    :param seconds: Time limit in seconds
    :return: Time limit in hh, mm, ss
    """
    # note: int won't round, eg: int(0.9) = 0
    hour = int(seconds / 3600)
    minute = int(seconds / 60 - hour * 60)
    return hour, minute


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


def get_highest_score(connection):
    sql_query = "SELECT max(score) FROM game"
    high_score = database_execute(connection, sql_query)
    return high_score[0]["max(score)"]


def calculate_score(player_state, score_param):
    score_money = round(score_param["money"] * player_state["money"])
    score_emission = round(score_param["emission"] * player_state["emission"])
    score_time = round(score_param["time"] * player_state["time"])
    score = score_money + score_time - score_emission
    player_state["score"] = score
    score_dict = {"money": score_money, "time": score_time, "emission": score_emission}
    return score_dict, score
