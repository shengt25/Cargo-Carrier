from enum import Enum


class Plane_Spec_Detail:
    def __init__(self, price, value, description):
        self.price = price
        self.value = value
        self.description = description


class Plane_Spec(Enum):
    FUEL = 1
    EMISSION = 2
    SPEED = 3
    PAYLOAD = 4


class Plane:
    def __init__(self, player, level: list):
        self.player = player
        self.upgrades = upgrades
        self.cargo_onboard = []  # init the cargo onboard

    def _upgrade(self, category: str):
        current_level = self.specs.get_level(category)
        next_level = current_level + 1
        if next_level > self.specs.get_max_level(category):
            return False, f"Sorry, {category} upgrade already at the maximum."
        else:
            expense = self.specs.plane_upgrade_data_json[category][next_level]["price"]
            if self.player.money < expense:
                return False, "No enough money."
            else:
                self.player.deduct_money(expense)
                return True, "Success."

    def upgrade_emission(self):
        current_level = self.specs.emission_level

        is_success, message = self._upgrade("emission")
        if is_success:
            self.specs.emission_level += 1
            self.specs.update_value()
        return is_success, message

    def upgrade_fuel(self):
        is_success, message = self._upgrade("fuel")
        if is_success:
            self.specs.fuel_level += 1
            self.specs.update_value()
        return is_success, message

    def upgrade_speed(self):
        is_success, message = self._upgrade("speed")
        if is_success:
            self.specs.speed_level += 1
            self.specs.update_value()
        return is_success, message

    def upgrade_payload(self):
        is_success, message = self._upgrade("payload")
        if is_success:
            self.specs.payload_level += 1
            self.specs.update_value()
        return is_success, message

    def get_weight_cargo_on(self):
        weight_cargo_on = 0
        for cargo in self.cargo_onboard:
            weight_cargo_on += cargo.weight
        return weight_cargo_on

    def load_cargo(self, cargo_loading):
        self.weight_cargo_on

        weight_cargo_on = self.get_weight_cargo_on

        weight_cargo_loading = 0
        for cargo in cargo_loading:
            weight_cargo_loading += cargo.weight

    def fly(self, cargo):
        cargo.dest
