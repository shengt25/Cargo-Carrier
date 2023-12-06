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
        fuel_consumption = round(distance * self.fuel_per_km)
        return fuel_consumption

    def calculate_time_consumption(self, ident):
        distance = self.calculate_distance(ident)
        time = round(distance / self.speed_per_h * 3600)
        return time

    def calculate_emission_consumption(self, ident):
        distance = self.calculate_distance(ident)
        emission_consumption = round(distance * self.emission_per_km)
        return emission_consumption

    def calculate_reward(self, ident):
        distance = self.calculate_distance(ident)
        reward = round(distance * self.reward_per_km)
        return reward

    def can_reach_fuel(self, ident):
        fuel_consumption = self.calculate_fuel_consumption(ident)
        fuel = self.player.fuel
        if fuel_consumption <= fuel:
            return True, fuel_consumption, fuel
        else:
            return False, fuel_consumption, fuel

    def can_reach_time(self, ident):
        time_consumption = self.calculate_time_consumption(ident)
        time = self.player.time
        if time_consumption <= time:
            return True, time_consumption, time
        else:
            return False, time_consumption, time

    def get_all_airports(self):
        for ident in self.airports.keys():
            if ident != self.player.location:
                success_reach_fuel, fuel_consumption, _ = self.can_reach_fuel(ident)
                success_reach_time, time_consumption, _ = self.can_reach_time(ident)
                reward = self.calculate_reward(ident)

                self.airports[ident]["reward"] = reward
                self.airports[ident]["fuel"] = fuel_consumption
                self.airports[ident]["time"] = time_consumption
                self.airports[ident]["emission"] = self.calculate_emission_consumption(ident)
                if success_reach_fuel:
                    self.airports[ident]["range-fuel"] = True
                else:
                    self.airports[ident]["range-fuel"] = False
                if success_reach_time:
                    self.airports[ident]["range-time"] = True
                else:
                    self.airports[ident]["range-time"] = False
        return self.airports

    def fly(self, ident):
        # TODO: validate ident
        if self.has_cargo:
            response = {"success": False,
                        "reason": "hack",
                        "message": "Unload first, hacker!"}
            return response
        else:
            success_reach_fuel, fuel_consumption, fuel = self.can_reach_fuel(ident)
            success_reach_time, time_consumption, time = self.can_reach_time(ident)
            if not success_reach_fuel and not success_reach_time:
                response = {"success": False,
                            "reason": "both",
                            "message": f"Not enough fuel and time, fuel needed: {fuel_consumption}, "
                                       f"time needed: {time_consumption}. You have {fuel} fuel and {time} time."}
                return response
            if not success_reach_time:
                response = {"success": False,
                            "reason": "time",
                            "message": f"Not enough time, time needed: {time_consumption}. You have {time} time."}
                return response
            elif not success_reach_fuel:
                response = {"success": False,
                            "reason": "fuel",
                            "message": f"Not enough fuel and time, fuel needed: {fuel_consumption}. "
                                       f"You have {fuel} fuel."}
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
