from Player import Player
from Plane import Plane
from AirportManager import AirportManager
from utils import Database
from Shop import Shop


class Game:
    def __init__(self, game_id, database_config, item_list, debug=False):
        self.game_id = game_id
        self.database = Database(database_config)

        self.player = Player(database=self.database, game_id=self.game_id, name="st", money=100000, fuel=100000,
                             time=800)
        self.airport_manager = AirportManager(self.database, self.player)
        self.shop = Shop(self.database, self.player, item_list)

