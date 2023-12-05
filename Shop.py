class Shop:
    def __init__(self, database, player, items, debug=False):
        self.database = database
        self.player = player
        self.items = items  # json
        self.debug = debug

    def buy_item(self, item, amount):
        response = {"success": False, "amount": 0, "expense": 0}

        expense = self.items[item]["price"] * amount
        if self.player.money >= expense:
            self.player.update_value(money_change=-expense)
            response["success"] = True
            response["amount"] = amount
            response["expense"] = expense
        return response

    def buy_fuel(self, amount):
        response = {"success": False, "amount": 0, "expense": 0}

        expense = self.items["fuel"]["price"] * amount
        if self.player.money >= expense:
            self.player.update_value(fuel_change=amount, money_change=-expense)
            response["success"] = True
            response["amount"] = amount
            response["expense"] = expense
        return response

    def buy_airport(self):
        response = {"success": False, "expense": 0}

        expense = self.items["airport"]["price"]
        if self.player.money >= expense:
            self.player.update_value(money_change=-expense)
            response["success"] = True
            response["expense"] = expense
        return response
