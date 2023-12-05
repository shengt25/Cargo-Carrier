from Player import Player
from Plane import Plane
from utils import Database, gen_airports
from Shop import Shop


class Game:
    def __init__(self, game_id, database_config, item_list, debug=False):
        self.game_id = game_id
        self.database = Database(database_config)
        self.player = Player(database=self.database, game_id=self.game_id, name="st", money=100000, fuel=100000,
                             time=800)
        self.shop = Shop(database=self.database, player=self.player, items=item_list)
        airports = gen_airports(database=self.database, player=self.player, number=10)
        self.plane = Plane(player=self.player, database=self.database, airports=airports,
                           fuel_per_km=0.1, speed_per_h=1.2, emission_per_km=1.2, reward_per_km=2, hire_cost=600)
