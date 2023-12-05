# API Testing Guide

### Start new game:

POST: `{"name": <name>}` 

To:  `<server>/game/new-game`

Response : `game id`



### Game page

Browser: `<server>/game/<game_id>`



### Get airports data:

GET:  `<server>/game/<game_id>/get-airports-data`

Response : `{}`



### Get players data:

GET:  `<server>/game/<game_id>/get-player-data`

Response : `{}`



### Get players and airports data:

GET:  `<server>/game/<game_id>/get-all-data`

Response : `{}`



### Buy fuel:

POST: `{"item": "fuel", "amount": <number>}` 

To: ``<server>/game/<game_id>/buy`

Response: `{}`



### Buy other things

POST: `{"item": <item_name>, "amount": <number>}` 

To:  ``<server>/game/<game_id>/buy`

Response : `game id`

Item names: 

- coffee
- airport

### Fly:

POST: `{"ident": <icao_code_of_airport>}` 

To: ``<server>/game/<game_id>/fly`

Response: `{}`



### Unload:

Send: POST `{"ident": <option>}` to ``<server>/game/<game_id>/unload`

Response : `{}`

Option: 

- 0: hire some else; 
- 1: roll dice

