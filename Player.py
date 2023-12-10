class Player:
    def __init__(self, database, game_id, name, money, fuel, time, verbose=False):
        self.database = database
        self.game_id = game_id
        self.name = name
        self.money = money
        self.fuel = fuel
        self.emission = 0
        self.location = ""
        self.time = time
        self.score = 0
        self.finish = False
        self.home = ""
        self.verbose = verbose
        self.hack_mode = False
        self.has_cargo = False

        sql_query = ("""INSERT INTO game (game_id, money, fuel, emission, location, time, screen_name, home, has_cargo, finish, score)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 0, 0, 0)""")
        parameter = self.game_id, self.money, self.fuel, self.emission, self.location, self.time, self.name, self.home
        self.database.query(sql_query, parameter)

    def update_value(self, fuel_change=None, emission_change=None, time_change=None, money_change=None):
        if fuel_change is not None:
            self.fuel += round(fuel_change)
        if emission_change is not None:
            self.emission += round(emission_change)
        if time_change is not None:
            self.time += round(time_change)
        if money_change is not None:
            self.money += round(money_change)

        sql_query = "UPDATE game SET fuel=%s, emission=%s, time=%s, money=%s WHERE game_id=%s"
        parameter = (self.fuel, self.emission, self.time, self.money, self.game_id)
        self.database.query(sql_query, parameter)

    def update_state(self, location=None, finish=None, score=None, home=None, has_cargo=None):
        if location is not None:
            self.location = location
        if finish is not None:
            self.finish = finish
        if score is not None:
            self.score = score
        if home is not None:
            self.home = home
        if has_cargo is not None:
            self.has_cargo = has_cargo

        sql_query = "UPDATE game SET location=%s, finish=%s, score=%s, home=%s, has_cargo=%s WHERE game_id=%s"
        parameter = (self.location, self.finish, self.score, self.home, self.has_cargo, self.game_id)
        self.database.query(sql_query, parameter)

    def get_all_data(self):
        response = {"name": self.name, "money": self.money, "fuel": self.fuel, "emission": self.emission,
                    "time": self.time, "location": self.location, "finish": self.finish, "score": self.score,
                    "home": self.home, "has_cargo": self.has_cargo}
        return response

    def update_all_data_from_database(self):
        # this function is mainly for modifying data manually (or hack)
        pass
