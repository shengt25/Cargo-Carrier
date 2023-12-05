class Player:
    def __init__(self, database, game_id, name, money, fuel, time, debug=False):
        self.database = database
        self.game_id = game_id
        self.name = name
        self.money = money
        self.fuel = fuel
        self.emission = 0
        self.location = ""
        self.time = time
        self.score = 0
        self.treasure_prob = 0
        self.treasure_found = 0
        self.finish = 0
        self.home = ""
        self.debug = debug
        sql_query = ("""INSERT INTO game (game_id, money, fuel, emission, location, 
                         treasure_prob, treasure_found, time, screen_name, home, finish, score)
                         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0)""")
        parameter = (self.game_id, self.money, self.fuel, self.emission, self.location, self.treasure_prob,
                     self.treasure_found, self.time, self.name, self.home)
        self.database.query(sql_query, parameter)

    def update_value(self, fuel_change=None, emission_change=None, time_change=None, money_change=None,
                     treasure_prob_change=None):
        if fuel_change is not None:
            self.fuel += round(fuel_change)
        if emission_change is not None:
            self.emission += round(emission_change)
        if time_change is not None:
            self.time += round(time_change)
        if money_change is not None:
            self.money += round(money_change)
        if treasure_prob_change is not None:
            self.treasure_prob += round(treasure_prob_change)
        sql_query = "UPDATE game SET fuel=%s, emission=%s, time=%s, money=%s, treasure_prob=%s WHERE game_id=%s"
        parameter = (self.fuel, self.emission, self.time, self.money, self.treasure_prob, self.game_id)
        self.database.query(sql_query, parameter)

    def update_state(self, location=None, treasure_found=None, finish=None, score=None, home=None):
        if location is not None:
            self.location = location
        if treasure_found is not None:
            self.treasure_found = treasure_found
        if finish is not None:
            self.finish = finish
        if score is not None:
            self.score = score
        if home is not None:
            self.home = home
        sql_query = "UPDATE game SET location=%s, treasure_found=%s, finish=%s, score=%s, home=%s WHERE game_id=%s"
        parameter = (self.location, self.treasure_found, self.finish, self.score, self.home, self.game_id)
        self.database.query(sql_query, parameter)

    def update_state_from_database(self):
        pass

    def get_state(self):
        response = {"money": self.money, "fuel": self.fuel, "emission": self.emission, "time": self.time,
                    "location": self.location, "treasure_prob": self.treasure_prob,
                    "treasure_found": self.treasure_found, "finish": self.finish, "score": self.score}
        return response
