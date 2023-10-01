from values import *


class Plane:
    def __init__(self, player):
        self.upgrade_list = upgrade_list
        self.player = player
        self.level = {
            "emission": 0,
            "fuel": 0,
            "speed": 0,
            "payload": 0
        }

    def _upgrade(self, name):
        current_level = self.level[name]
        next_level = current_level + 1
        if next_level > len(self.upgrade_list[name]):
            return False, f"Sorry, {name} upgrade already at the maximum."
        else:
            expense = self.upgrade_list[name][next_level]["price"]
            if self.player.money < expense:
                return False, "No enough money."
            else:
                self.player.use_money(expense)
                self.level[name] = next_level
                return True, "Success."

    def upgrade_emission(self):
        self._upgrade("emission")

    def upgrade_fuel(self):
        self._upgrade("fuel")

    def upgrade_speed(self):
        self._upgrade("speed")

    def upgrade_payload(self):
        self._upgrade("payload")
