from enum import Enum


class Player:
    def __init__(self, name, init_money, init_emission, init_fuel):
        self.name = name
        self.money = init_money
        self.emission = init_emission
        self.fuel = init_fuel

    def use_money(self, amount):
        """
        Balance will be checked before using.
        :return: True/False (success/fail)
        """
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def add_money(self, amount):
        """
        Add money to player.
        :param amount: number of money
        :return: True/False (success/fail)
        """
        self.money += amount
        return self.money

# todo use dict to store attribute, easy for future update. But keep the Plane_Spec and Spec class to store
# also, use specs_file to create dict current file
