from geopy.distance import distance as geo_distance  # prevent shadow_name warning (distance is name of variable)
import random


class Plane:
    def __init__(self, player, database, airports, fuel_per_km, speed_per_h, emission_per_km, reward_per_km,
                 hire_cost, debug=False):
        self.player = player
        self.airports = airports
        self.accessibility = {}
        self.database = database

        self.fuel_per_km = fuel_per_km
        self.speed_per_h = speed_per_h
        self.emission_per_km = emission_per_km
        self.reward_per_km = reward_per_km

        self.hire_cost = hire_cost

        self.debug = debug

    def calculate_distance(self, ident1: str, ident2: str) -> float:
        """Calculate distance with two ident
        :param ident1: ident of first airport
        :param ident2: ident of first airport
        :return: Rounded distance (float, with 2 decimal)"""
        coordinates1 = (self.airports[ident1]["latitude_deg"], self.airports[ident1]["longitude_deg"])
        coordinates2 = (self.airports[ident2]["latitude_deg"], self.airports[ident2]["longitude_deg"])
        airports_distance = geo_distance(coordinates1, coordinates2).km
        return round(airports_distance)

    def calculate_fuel_consumption(self, ident1, ident2):
        distance = self.calculate_distance(ident1, ident2)
        fuel_consumption = distance * self.fuel_per_km
        return fuel_consumption

    def calculate_time_consumption(self, ident1, ident2):
        distance = self.calculate_distance(ident1, ident2)
        time = distance / self.speed_per_h * 3600
        return time

    def calculate_emission_consumption(self, ident1, ident2):
        distance = self.calculate_distance(ident1, ident2)
        emission_consumption = distance * self.emission_per_km
        return emission_consumption

    def can_reach_fuel(self, ident1, ident2):
        fuel_consumption = self.calculate_fuel_consumption(ident1, ident2)
        fuel = self.player.fuel
        if fuel_consumption <= fuel:
            return True
        else:
            return False

    def can_reach_time(self, ident1, ident2):
        time_consumption = self.calculate_time_consumption(ident1, ident2)
        time = self.player.time
        if time_consumption <= time:
            return True
        else:
            return False

    def get_airports_accessibility(self):
        airports_accessibility = {}
        for ident in self.airports.keys():
            if ident != self.player.location:
                airports_accessibility[ident] = {}
                if self.can_reach_fuel(self.player.location, ident):
                    airports_accessibility[ident]["fuel"] = True
                else:
                    airports_accessibility[ident]["fuel"] = False
                if self.can_reach_time(self.player.location, ident):
                    airports_accessibility[ident]["time"] = True
                else:
                    airports_accessibility[ident]["time"] = False
        self.accessibility = airports_accessibility
        return airports_accessibility

    def fly(self, ident):
        # check if enough fuel and time for destination
        if not self.can_reach_fuel(self.player.location, ident):
            return {"success": False}

        if not self.can_reach_time(self.player.location, ident):
            return {"success": False}

        response = {"success": True, "update_detector": False, "new_prob": 0}

        fuel_consumption = self.calculate_fuel_consumption(self.player.location, ident)
        emission_consumption = self.calculate_emission_consumption(self.player.location, ident)
        time_consumption = self.calculate_time_consumption(self.player.location, ident)

        self.player.update_value(fuel_change=-fuel_consumption, emission_change=emission_consumption,
                                 time_change=-time_consumption)
        self.player.update_state(location=ident)

        # if not visited, update visit and update detector
        if self.airports[ident]["visit"] == 0:
            self.airports[ident]["visit"] = 1
            sql_query = "UPDATE game_airport SET visit=1 WHERE game_id=%s AND ident=%s"
            parameter = (self.player.game_id, ident)
            self.database.query(sql_query, parameter)

            # # update detector
            # distance = self.calculate_distance(self.player.location, ident)
            # new_prob = self._update_detector(distance)
            # self.player.treasure_prob = new_prob
            # response["update_detector"] = True
            # response["new_prob"] = new_prob
            # sql_query = "UPDATE game SET treasure_prob=%s WHERE game_id=%s"
            # parameter = (new_prob, self.player.game_id)
            # self.database.query(sql_query, parameter)

        return response

    def unload(self, option):
        response = {"success": False, "money_change": 0}
        if option == 0:
            self.player.update_value(money_change=-self.hire_cost)
            response["success"] = True
            response["money_change"] = -self.hire_cost
        else:
            result = random.randint(1, 6)
            if result == 1:
                response["money_change"] = -self.player.money * 0.9
            elif result == 2:
                response["money_change"] = -1500
            elif result == 3:
                response["money_change"] = 0
            elif result == 4:
                response["money_change"] = 1500
            elif result == 5:
                response["money_change"] = 1800
            elif result == 6:
                response["money_change"] = self.player.money
            response["success"] = True
            self.player.update_value(money_change=response["money_change"])
        return response

    # def _update_detector(self, distance):
    #     prob_up = self.detector_prob_per_10k_km * distance / 10000
    #     self.player.update_value(treasure_prob_change=prob_up)
    #     return self.player.treasure_prob
    #
    # def detect(self):
    #     response = {"success": False, "money_change": 0}
    #     detection = random.randint(1, 10000)
    #     if detection <= self.player.treasure_prob:
    #         self.player.update_state(treasure_found=1)
    #         self.player.update_value(money_change=20000)
    #         response["success"] = True
    #         response["money_change"] = 20000
    #     return response
