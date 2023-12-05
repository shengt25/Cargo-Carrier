from geopy.distance import distance as geo_distance  # prevent shadow_name warning (distance is name of variable)
import random


class Plane:
    def __init__(self, player, database, airports, fuel_per_km, speed_per_h, emission_per_km, reward_per_km,
                 hire_cost, verbose=False):
        self.player = player
        self.airports = airports
        self.database = database

        self.fuel_per_km = fuel_per_km
        self.speed_per_h = speed_per_h
        self.emission_per_km = emission_per_km
        self.reward_per_km = reward_per_km

        self.hire_cost = hire_cost

        self.verbose = verbose

        self.has_cargo = False
        self.accessibility = {}

    def calculate_distance(self, ident: str) -> float:
        coordinates1 = (self.airports[self.player.location]["latitude_deg"],
                        self.airports[self.player.location]["longitude_deg"])
        coordinates2 = (self.airports[ident]["latitude_deg"],
                        self.airports[ident]["longitude_deg"])
        airports_distance = geo_distance(coordinates1, coordinates2).km
        return round(airports_distance)

    def calculate_fuel_consumption(self, ident):
        distance = self.calculate_distance(ident)
        fuel_consumption = distance * self.fuel_per_km
        return fuel_consumption

    def calculate_time_consumption(self, ident):
        distance = self.calculate_distance(ident)
        time = distance / self.speed_per_h * 3600
        return time

    def calculate_emission_consumption(self, ident):
        distance = self.calculate_distance(ident)
        emission_consumption = distance * self.emission_per_km
        return emission_consumption

    def can_reach_fuel(self, ident):
        fuel_consumption = self.calculate_fuel_consumption(ident)
        fuel = self.player.fuel
        if fuel_consumption <= fuel:
            return True
        else:
            return False

    def can_reach_time(self, ident):
        time_consumption = self.calculate_time_consumption(ident)
        time = self.player.time
        if time_consumption <= time:
            return True
        else:
            return False

    def get_all_airports_accessibility(self):
        airports_accessibility = {}
        for ident in self.airports.keys():
            if ident != self.player.location:
                airports_accessibility[ident] = {}
                if self.can_reach_fuel(ident):
                    airports_accessibility[ident]["fuel"] = True
                else:
                    airports_accessibility[ident]["fuel"] = False
                if self.can_reach_time(ident):
                    airports_accessibility[ident]["time"] = True
                else:
                    airports_accessibility[ident]["time"] = False
        self.accessibility = airports_accessibility
        return airports_accessibility

    def get_all_airports(self):
        return self.airports

    def fly(self, ident):
        if self.has_cargo:
            response = {"success": False,
                        "reason": "hack",
                        "message": "Unload first, hacker!"}
            return response
        else:
            can_reach_fuel = self.can_reach_fuel(ident)
            can_reach_time = self.can_reach_time(ident)
            if not can_reach_fuel and not can_reach_time:
                response = {"success": False,
                            "reason": "both",
                            "message": "Not enough fuel and time"}
                return response
            if not self.can_reach_time(ident):
                response = {"success": False,
                            "reason": "time",
                            "message": "Not enough time"}
                return response
            elif not self.can_reach_fuel(ident):
                response = {"success": False,
                            "reason": "fuel",
                            "message": "Not enough fuel and time"}
                return response

            self.has_cargo = True
            # calculate consumption
            fuel_consumption = self.calculate_fuel_consumption(ident)
            emission_consumption = self.calculate_emission_consumption(ident)
            time_consumption = self.calculate_time_consumption(ident)
            # update player's value and state
            self.player.update_value(fuel_change=-fuel_consumption, emission_change=emission_consumption,
                                     time_change=-time_consumption)
            self.player.update_state(location=ident)

            # if not visited, update visit
            if self.airports[ident]["visit"] == 0:
                self.airports[ident]["visit"] = 1
                sql_query = "UPDATE game_airport SET visit=1 WHERE game_id=%s AND ident=%s"
                parameter = (self.player.game_id, ident)
                self.database.query(sql_query, parameter)
            response = {"success": True,
                        "player": self.player.get_all_data(),
                        "message": "You can now unload."}
            return response

    def unload(self, option):
        if not self.has_cargo:
            response = {"success": False,
                        "message": "How do you unload without cargo, hacker?"}
        else:
            self.has_cargo = False
            if option == 0:
                self.player.update_value(money_change=-self.hire_cost)
                response = {"success": True,
                            "option": option,
                            "player": self.player.get_all_data(),
                            "message": ""}
            else:
                dice_result = random.randint(1, 6)
                if dice_result == 1:
                    self.player.update_value(money_change=-self.player.money * 0.9)
                elif dice_result == 2:
                    self.player.update_value(money_change=-1500)
                elif dice_result == 3:
                    pass
                elif dice_result == 4:
                    self.player.update_value(money_change=1500)
                elif dice_result == 5:
                    self.player.update_value(money_change=1800)
                elif dice_result == 6:
                    self.player.update_value(money_change=self.player.money)
                response = {"success": True,
                            "dice": dice_result,
                            "player": self.player.get_all_data(),
                            "message": ""}
        return response
