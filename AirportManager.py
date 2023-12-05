class AirportManager:
    def __init__(self, database, player, debug=False):
        self.database = database
        self.player = player
        self.airports = {}
        self.debug = debug

    def gen_airports(self, number):
        """
        Generate random airports and save to database, no return.
        :param number: The number of airports desired
        """
        # get random airports
        sql_query = """SELECT ident, airport.iso_country, airport.name, country.name as country_name, latitude_deg, longitude_deg
                        FROM airport
                        JOIN country on airport.iso_country = country.iso_country
                        WHERE airport.continent = 'EU'
                        AND type = 'large_airport'
                        ORDER BY RAND()
                        LIMIT %s"""
        response = self.database.query(sql_query, number)

        # save to dictionary
        home_set = False
        for airport in response:
            ident = airport["ident"]
            del airport["ident"]
            # set home airport and current airport
            if not home_set:
                self.player.update_state(home=ident, location=ident)
                airport["visit"] = 1
                home_set = True
            else:
                airport["visit"] = 0
            self.airports[ident] = airport

        # save to database
        for ident in self.airports.keys():
            airport = self.airports[ident]
            parameter = (self.player.game_id, airport["iso_country"], airport["country_name"], ident,
                         airport["name"], airport["latitude_deg"], airport["longitude_deg"], airport["visit"])

            sql_query = """INSERT INTO game_airport (game_id, iso_country, country_name, ident, name, 
                            latitude_deg, longitude_deg, visit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            self.database.query(sql_query, parameter)

    def get_airports(self):
        return self.airports
