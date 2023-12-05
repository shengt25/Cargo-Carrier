from Player import Player
from Plane import Plane
from utils import Database, gen_airports
from Shop import Shop


class Game:
    def __init__(self, game_id, database_param, shop_param, player_name, airport_number, player_param, plane_param,
                 verbose=False):
        self.game_id = game_id
        self.database = Database(database_param)
        self.player = Player(database=self.database, game_id=self.game_id, name=player_name,
                             money=player_param["money"], fuel=player_param["fuel"], time=player_param["time"])
        self.shop = Shop(database=self.database, player=self.player, items=shop_param)
        airports = gen_airports(database=self.database, player=self.player, number=airport_number)
        self.plane = Plane(player=self.player, database=self.database, airports=airports,
                           fuel_per_km=plane_param["fuel_per_km"],
                           speed_per_h=plane_param["speed_per_h"],
                           emission_per_km=plane_param["emission_per_km"],
                           reward_per_km=plane_param["reward_per_km"],
                           hire_cost=plane_param["hire_cost"], )
