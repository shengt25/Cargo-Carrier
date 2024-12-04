## Getting Started

### Install the required packages:

```
pip install geopy mysql-connector-python flask
```

### Import Database 

Create a new database and import data from provided `database.sql`.

### Configure Database in app.py

At the beginning of app.py there are configerations about database and game settings.  Modify them as your database configuration.

```
database_param = {"host": "127.0.0.1",
                  "user": "root",
                  "password": "pwd",
                  "database": "cargo_carrier",
                  "port": 3306}
```

### Run App

Run `python app.py`.

# Backend API Documentation 

### To Start new game:

POST: `{"name": <name>}` 

To:  `<server>/game/new-game`

For example: send `{"name": Amir}` to `https://st17.fyigame/game/new-`

Example response: 

`{ "gameID": "8fa7a7482e6376395e8771501a946d8a8edf7689", "message": "[ok] creating new game", "success": true }`



### To Get Game Page

In browser: `<server>/game/<game_id>`

Response: the web page of game that belongs to `<game_id> `



### To Get Airports Data:

GET:  `<server>/game/<game_id>/get-airports-data`

Example response: 

`{"success": false, "message": "[fail] get-airports-data: game not found" }` 

or

```json
{"airports": {
    		"message": "[ok] get-airports-data",
    		"success": true
        "EDDH": {
            "country_name": "Germany",
            "current": false,
            "distance": 340,
            "emission": 34,
            "fuel": 408,
            "ident": "EDDH",
            "iso_country": "DE",
            "latitude_deg": 53.630402,
            "longitude_deg": 9.98823,
            "name": "Hamburg Helmut Schmidt Airport",
            "range_fuel": true,
            "range_time": true,
            "reward": 408,
            "time": 0.4,
            "visit": 0},
				}
}
```



### Get players data:

GET:  `<server>/game/<game_id>/get-player-data`

Example response: 

`{ "message": "[fail] get-player-data: game not found", "success": false }`

or

```json
{"message": "[ok] get-player-data",
    "player": {
        "emission": 0,
        "finish": false,
        "fuel": 1000,
        "has_cargo": false,
        "home": "EDDL",
        "location": "EDDL",
        "money": 2000,
        "name": "amir",
        "score": 0,
        "time": 240
    },
    "success": true}
```



### To Buy fuel:

POST: `{"item": "fuel", "amount": <number>}` 

To: `<server>/game/<game_id>/buy`

Example response: 

`{"message": "[fail] buy: game not found", "reason": "game", "success": false }`

or

`{ "message": "[fail] buy: airport", "reason": "money", "success": false }`

or

```
{"message": "[ok] buy: airport",
    		"success": true
    "player": {
        "emission": 0,
        "finish": false,
        "fuel": 1000,
        "has_cargo": false,
        "home": "LBBG",
        "location": "LBBG",
        "money": 0,
        "name": "t",
        "score": 0,
        "time": 240
    },}
```



### To Buy other things

POST: `{"item": <item_name>, "amount": <number>}` 

To:  `<server>/game/<game_id>/buy`

Response: same as above, except for item names are different.

Item name list: 

- coffee

- airport

  

### To Fly:

POST: `{"ident": <icao_code_of_airport>}` 

To: ``<server>/game/<game_id>/fly`

Response: 

`{ "message": "Not enough fuel and time, fuel needed: 1070. You have 1000 fuel.", "reason": "fuel", "success": false }`

or

`{ "message": "Not enough fuel and time, fuel needed: 1958, time needed: 2.0. You have 1000 fuel and 0 time.", "reason": "both", "success": false }`

or

```
{"message": "You fly to EGGW and now you can unload.",
    "player": {
        "emission": 78,
        "finish": false,
        "fuel": 59,
        "has_cargo": 1,
        "home": "LFBD",
        "location": "EGGW",
        "money": 20941,
        "name": "amir",
        "score": 0,
        "time": 239
    },
    "success": true}
```

> **Note** : Special cases when trying to land where they already at; flying again before unloading or flying to somewhere that does not exist on the map(due to modified html element, javascript or sending wrong data)
These are the responses for such cases:

`{ "message": "You are already here, hacker!", "reason": "airport", "success": false }`

`{ "message": "Unload first, hacker!", "reason": "hack", "success": false }`

`{ "message": "Airport not found, what's wrong with the programmer?", "reason": "airport", "success": false }`



### To Unload:

Send: POST `{"ident": <option>}` to ``<server>/game/<game_id>/unload`

Option: 

- 0: hire some else
- 1: roll dice, and the result will also be returned

Example response:

```
{"message": "You choose to hire",
    "option": 0,
    "player": {
        "emission": 117,
        "finish": false,
        "fuel": 8595,
        "has_cargo": false,
        "home": "LWSK",
        "location": "EDDN",
        "money": 20805,
        "name": "amir",
        "score": 0,
        "time": 238
    },
    "success": true}
```

or

```
{"dice": 6,
  "message": "You choose to unload yourself",
  "player": {
    "emission": 198,
    "finish": false,
    "fuel": 7623,
    "has_cargo": false,
    "home": "LWSK",
    "location": "EGSS",
    "money": 43554,
    "name": "amir",
    "score": 0,
    "time": 237
  },
  "success": true}
```

There are error cases when trying to unload again before flying. (for example because someone modified javascript or send wrong data)
It gives response message like this:
`{ "message": "How do you unload without cargo, hacker?", "success": false }`
