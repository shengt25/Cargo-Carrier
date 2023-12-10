from geopy.distance import distance as geo_distance  # prevent shadow_name warning (distance is name of variable)
import random


class Plane:
    def __init__(self, player, database, airports, fuel_per_km, speed_per_h, emission_per_km, reward_per_km,
                 hire_cost, fuel_price, verbose=False):
        self.player = player
        self.airports = airports
        self.database = database

        self.fuel_per_km = fuel_per_km
        self.speed_per_h = speed_per_h
        self.emission_per_km = emission_per_km
        self.reward_per_km = reward_per_km

        self.hire_cost = hire_cost

        self.verbose = verbose
        self.fuel_price = fuel_price

        self.update_all_airports()

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
        time = round(distance / self.speed_per_h, 1)
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

    def update_all_airports(self):
        # can_go_somewhere = 0
        for ident in self.airports:
            if ident == self.player.location:
                # exclude current airport, set to be false
                self.airports[ident]["range_fuel"] = False
                self.airports[ident]["range_time"] = False
                self.airports[ident]["current"] = True
            else:
                success_reach_fuel, fuel_consumption, _ = self.can_reach_fuel(ident)
                success_reach_time, time_consumption, _ = self.can_reach_time(ident)
                reward = self.calculate_reward(ident)
                self.airports[ident]["current"] = False
                self.airports[ident]["distance"] = self.calculate_distance(ident)
                self.airports[ident]["reward"] = reward
                self.airports[ident]["fuel"] = fuel_consumption
                self.airports[ident]["time"] = time_consumption
                self.airports[ident]["emission"] = self.calculate_emission_consumption(ident)
                if success_reach_fuel:
                    self.airports[ident]["range_fuel"] = True
                    # can_go_somewhere += 1
                else:
                    self.airports[ident]["range_fuel"] = False
                if success_reach_time:
                    self.airports[ident]["range_time"] = True
                    # can_go_somewhere += 1
                else:
                    self.airports[ident]["range_time"] = False
        # if can_go_somewhere == 0:  # todo what is this for?
        #     self.check_money_ending()
        #     self.check_time_ending()

    def get_all_airports(self):
        self.update_all_airports()
        return self.airports

    def check_money_ending(self):
        can_go_somewhere = 0
        money = self.player.money
        fuel_buy = money / self.fuel_price
        fuel_left = self.player.fuel
        fuel = fuel_left + fuel_buy
        for ident in self.airports:
            if ident != self.player.location:
                fuel_consumption = self.calculate_fuel_consumption(ident)
                if fuel_consumption <= fuel:
                    can_go_somewhere += 1
        if can_go_somewhere == 0:
            self.player.update_state(finish=True)
            return True, f"[ok] check-ending With all money {money} you can have {fuel_left} + {fuel_buy} fuel, you can't go anywhere, game over."
        else:
            return False, f"[ok] check-ending With all money {money} you can have {fuel_left} + {fuel_buy} fuel, game continues."

    def check_time_ending(self):
        can_go_somewhere = 0
        time_left = self.player.time
        for ident in self.airports:
            if ident != self.player.location:
                time_consumption = self.calculate_time_consumption(ident)
                if time_consumption <= time_left:
                    can_go_somewhere += 1
        if can_go_somewhere == 0:
            self.player.update_state(finish=True)
            return True, f"[ok] check-ending With all {time_left} you can't go anywhere, game over."
        else:
            return False, f"[ok] check-ending With all {time_left}, game continues."

    def fly(self, ident):
        if self.player.has_cargo:
            response = {"success": False,
                        "reason": "hack",
                        "message": "Unload first, hacker!"}
            return response

        if ident == self.player.location:
            response = {"success": False,
                        "reason": "airport",
                        "message": "You are already here, hacker!"}
            return response

        if ident not in self.airports.keys():
            response = {"success": False,
                        "reason": "airport",
                        "message": "Airport not found, what's wrong with the programmer?"}
            return response

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
        self.player.update_state(has_cargo=1)

        # calculate consumption
        fuel_consumption = self.airports[ident]["fuel"]
        emission_consumption = self.airports[ident]["emission"]
        time_consumption = self.airports[ident]["time"]
        reward = self.airports[ident]["reward"]

        # update player's value and state
        last_ident = self.player.location
        self.airports[last_ident]["current"] = False
        self.airports[ident]["current"] = True
        self.player.update_value(fuel_change=-fuel_consumption, emission_change=emission_consumption,
                                 time_change=-time_consumption, money_change=reward)
        self.player.update_state(location=ident)

        # if not visited, update visit
        if self.airports[ident]["visit"] == 0:
            self.airports[ident]["visit"] = 1
            sql_query = "UPDATE game_airport SET visit=1 WHERE game_id=%s AND ident=%s"
            parameter = (self.player.game_id, ident)
            self.database.query(sql_query, parameter)
        response = {"success": True,
                    "player": self.player.get_all_data(),
                    "message": f"You fly to {ident} and now you can unload."}
        self.update_all_airports()
        return response

    def unload(self, option):
        if not self.player.has_cargo:
            response = {"success": False,
                        "message": "How do you unload without cargo, hacker?"}
        else:
            if option == 0 or option == "0":
                if self.player.money < self.hire_cost:
                    response = {"success": False,
                                "reason": "money",
                                "message": "Not enough money to hire."}
                    return response
                else:
                    self.player.update_value(money_change=-self.hire_cost)
                    self.player.has_cargo = False
                    response = {"success": True,
                                "option": option,
                                "player": self.player.get_all_data(),
                                "message": "You choose to hire"}
            else:
                self.player.has_cargo = False
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

                # reset money to be 0 if less than 0, if choose dice
                if self.player.money < 0:
                    self.player.money = 0
                response = {"success": True,
                            "dice": dice_result,
                            "player": self.player.get_all_data(),
                            "message": "You choose to unload yourself"}
        return response
