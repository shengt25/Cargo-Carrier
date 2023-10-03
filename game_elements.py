from enum import Enum
import json


class Airport_List(Enum):
    HELSINKI = 1
    PARIS = 2


class Cargo_Type(Enum):
    WOOD = 1
    METAL = 2


def load_all_cargo_metadata(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
    all_cargo_metadata_enum = {}
    all_cargo_metadata_str = data.get("cargos", [])
    for cargo_name in all_cargo_metadata_str:
        cargo_name_enum = Cargo_Type[cargo_name.upper()]
        attributes = {
            "price": all_cargo_metadata_str[cargo_name]["price"],
            "weight": all_cargo_metadata_str[cargo_name]["weight"],
            "size": all_cargo_metadata_str[cargo_name]["size"],
            "description": all_cargo_metadata_str[cargo_name]["description"],
        }
        all_cargo_metadata_enum[cargo_name_enum] = attributes
    return all_cargo_metadata_enum


def create_cargo(cargo_type: Cargo_Type, all_cargo_metadata: dict, dest: str):
    # weight = data
    return Cargo(cargo_type, all_cargo_metadata[cargo_type]["weight"], all_cargo_metadata[cargo_type]["size"],
                 all_cargo_metadata[cargo_type]["price"],
                 all_cargo_metadata[cargo_type]["description"], dest)


class Cargo:
    def __init__(self, cargo_type, weight, size, price, description, dest=None):
        # using cargo_type instead of type, because type is a built-in name
        self.cargo_type = cargo_type
        self.weight = weight
        self.size = size
        self.dest = dest
        self.price = price
        self.description = description

    @staticmethod
    def load_cargo_types(cargo_type_data):
        cargos = []
        for cargo_data in cargo_type_data:
            # cargo_type is a string loaded from cargo_type_data
            cargo_type = Cargo_Type[cargo_data.upper()]  # string to enum
            price = cargo_type_data[cargo_data]["price"]
            weight = cargo_type_data[cargo_data]["weight"]
            size = cargo_type_data[cargo_data]["size"]
            description = cargo_type_data[cargo_data]["description"]
            cargo = Cargo(cargo_type, weight, size, price, description)
            cargos.append(cargo)
        return cargos


class Store:
    def __init__(self, store_items):
        pass


class Player:
    def __init__(self, name, init_money, init_emission, init_fuel):
        self.name = name
        self.money = init_money
        self.emission = init_emission
        self.fuel = init_fuel

    def buy_fuel(self, amount):
        expense = price_data["fuel"] * amount
        return self.use_money(expense)

    def buy_emission(self, amount):
        expense = price_data["emission"] * amount
        return self.use_money(expense)

    def use_money(self, amount):
        """
        Balance will be checked before using.
        :return: True/False (success/fail)
        """
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def use_emission(self, amount):
        self.emission += amount
        return self.emission

    def use_fuel(self, amount):
        self.fuel += amount
        return self.fuel

    def add_money(self, amount):
        """
        Add money to player.
        :param amount: number of money
        :return: True/False (success/fail)
        """
        self.money += amount
        return self.money

    def add_emission(self, amount):
        self.emission += amount
        return self.emission

    def add_fuel(self, amount):
        self.fuel += amount
        return self.fuel


# todo use dict to store attribute, easy for future update. But keep the Plane_Spec and Spec class to store
# also, use specs_file to create dict current file

class Plane:
    def __init__(self, player, upgrades):
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
