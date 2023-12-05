from Player import Player
from Plane import Plane
from utils import Database

if __name__ == "__main__":
    local_database_config = {"host": "127.0.0.1",
                             "user": "root",
                             "password": "metro",
                             "database": "cargo_carrier",
                             "port": 3306}
    database = Database(local_database_config)

    player = Player(database, "7", "st", 100000, 100000, 1.2, 800, 0.1, 1.2)

    airport = AirportManager(database, player)

    airport.gen_airports(10)
    print(airport.get_airports())
    print(plane.get_airports_accessibility())
