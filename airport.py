from utils import database_execute
from geopy.distance import distance as geo_distance  # prevent shadow_name warning (distance is name of variable)


# ---------------------
# AIRPORT
# ---------------------
def generate_random_airports(connection, num: int) -> dict:
    """
    Generate random airports and save to database, no return.
    :param connection: SQL connection
    :param num: The number of airports desired
    """
    # get random airports
    sql_query = """
    SELECT airport.iso_country, ident, airport.name, country.name as country_name, latitude_deg, longitude_deg
    FROM airport
    JOIN country on airport.iso_country = country.iso_country
    WHERE airport.continent = 'EU'
    AND type = 'large_airport'
    ORDER BY RAND()
    LIMIT %s
    """
    airport_info_dict = database_execute(connection, sql_query, (num,))

    # delete last random airports
    sql_query = "DELETE FROM game_airport"
    database_execute(connection, sql_query)
    home_airport = None
    # save to database
    # the first airport is home
    home_marked = False
    for airport_info in airport_info_dict:
        if not home_marked:
            sql_query = """INSERT INTO game_airport 
            (iso_country, country_name, ident, name, latitude_deg, longitude_deg, visit) 
            VALUES (%s, %s, %s, %s, %s, %s, 2)"""
            home_marked = True
            home_airport = airport_info
        else:
            sql_query = """INSERT INTO game_airport 
            (iso_country, country_name, ident, name, latitude_deg, longitude_deg, visit) 
            VALUES (%s, %s, %s, %s, %s, %s, 0)"""
        parameter = (
            airport_info["iso_country"], airport_info["country_name"], airport_info["ident"], airport_info["name"],
            airport_info["latitude_deg"], airport_info["longitude_deg"])
        database_execute(connection, sql_query, parameter)
        home_airport["visit"] = 2
    return home_airport


def get_airports_distance(connection, first_airport_icao: str, second_airport_icao: str) -> float:
    """Calculate distance with two ICAO
    :param connection: SQL connection
    :param first_airport_icao: ICAO of first airport
    :param second_airport_icao: ICAO of first airport
    :return: Rounded distance (float, with 2 decimal)"""
    sql_query = "SELECT latitude_deg , longitude_deg FROM airport WHERE ident = %s OR ident = %s"
    response = database_execute(connection, sql_query, (first_airport_icao, second_airport_icao))
    first_airport_coordinates = response[0]["latitude_deg"], response[0]["longitude_deg"]
    second_airport_coordinates = response[1]["latitude_deg"], response[1]["longitude_deg"]

    airports_distance = geo_distance(first_airport_coordinates, second_airport_coordinates).km
    return round(airports_distance)


def get_airports_in_range(connection, plane_param, player_state: dict) -> tuple[dict, list, list, bool]:
    """
    Return airports in order, by distance
    :param plane_param: Plane's fuel, speed, etc.
    :param connection: SQL connection
    :param player_state: Player state dictionary
    :return: List of dictionary: [{ident, name, country_name, visit, distance, fuel_consumption}, {...}, ...]
    """
    fuel = player_state["fuel"]
    range_by_fuel = round(fuel / plane_param["fuel_consumption"])
    range_by_time = round(plane_param["speed"] * player_state["time"] / 3600)
    # plane_speed: km/h ==> plane_speed/3600: km/s

    sql_query = "SELECT ident, name, country_name, visit FROM game_airport"
    airport_info_list = database_execute(connection, sql_query)
    player_icao = player_state["location"]
    airports_in_range = []
    airports_out_of_range = []
    airport_now = None

    # assume no time to fly anywhere, will check is it true, later.
    flag_no_time = True

    for airport_info in airport_info_list:
        dest_icao = airport_info["ident"]
        if dest_icao == player_icao:
            airport_now = airport_info
        else:
            distance = get_airports_distance(connection, player_icao, dest_icao)
            airport_info["distance"] = distance
            airport_info["time"] = round(distance / plane_param["speed"] * 3600)  # time is in second
            airport_info["fuel_consumption"] = round(distance * plane_param["fuel_consumption"])
            airport_info["emission"] = round(distance * plane_param["emission"])
            airport_info["reward"] = round(airport_info["distance"] * plane_param["reward"])

            # if anywhere is in range of time, set flag_no_time to False
            if distance <= range_by_time:
                flag_no_time = False
                # then check fuel range
                if distance <= range_by_fuel:
                    airports_in_range.append(airport_info)
                else:
                    airports_out_of_range.append(airport_info)
    airports_in_range.sort(key=lambda x: x["distance"])
    airports_out_of_range.sort(key=lambda x: x["distance"])
    if airport_now is None:
        raise Exception("Cannot get current airport, please restart the game.")
    return airport_now, airports_in_range, airports_out_of_range, flag_no_time


def mark_visit_airport(connection, selected_airport):
    if selected_airport["visit"] == 0:
        sql_query = "UPDATE game_airport SET visit=1 WHERE ident=%s"
        database_execute(connection, sql_query, (selected_airport["ident"],))
