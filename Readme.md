# Backend API Ussage Guide

## Replace server with server address

The server address can be `http://127.0.0.1:5000` when you run it locally

Or you can just use `https://st17.fyi`, it is published in online server.

## Test using Postman or others

### Start new game:

POST: `{"name": <name>}` 

To:  `<server>/game/new-game`

For example: send `{"name": Amir}` to `https://st17.fyi/game/new-game`

Example response: 

`{ "gameID": "8fa7a7482e6376395e8771501a946d8a8edf7689", "message": "[ok] creating new game", "success": true }`



### Game page

In browser: `<server>/game/<game_id>`

Response: the web page of game that belongs to `<game_id> `



### Get airports data:

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
        ... ...(more airports data inside ICAO code as json key)}
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



### Buy fuel:

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



### Buy other things

POST: `{"item": <item_name>, "amount": <number>}` 

To:  `<server>/game/<game_id>/buy`

Response: same as above, except for item names are different.

Item name list: 

- coffee

- airport

  

### Fly:

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

Special case when trying to where they already at, fly again before unload or to somewhere does not exist in map(for example because someone modified html element, javascript or send wrong data)

`{ "message": "You are already here, hacker!", "reason": "airport", "success": false }`

`{ "message": "Unload first, hacker!", "reason": "hack", "success": false }`

`{ "message": "Airport not found, what's wrong with the programmer?", "reason": "airport", "success": false }`



### Unload:

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

Special case when trying to unload again before flying. (for example because someone modified javascript or send wrong data)

`{ "message": "How do you unload without cargo, hacker?", "success": false }`
