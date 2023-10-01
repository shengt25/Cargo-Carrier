from values import *


class Player:
    def __init__(self, name, init_money, init_emission, init_fuel):
        self.name = name
        self.money = init_money
        self.emission = init_emission
        self.fuel = init_fuel

    def add_money(self, amount):
        self.money += amount
        return self.money

    def use_money(self, amount):
        self.money -= amount
        return self.money

    def add_emission(self, amount):
        self.emission += amount
        return self.emission

    def use_emission(self, amount):
        self.emission += amount
        return self.emission

    def add_fuel(self, amount):
        self.fuel += amount
        return self.fuel

    def use_fuel(self, amount):
        self.fuel += amount
        return self.fuel

    def buy_fuel(self, amount):
        expense = price_list["fuel"] * amount
        if self.money < expense:
            return False
        else:
            self.use_money(expense)
            self.add_fuel(amount)
            return True

    def buy_emission(self, amount):
        expense = price_list["emission"] * amount
        if self.money < expense:
            return False
        else:
            self.use_money(expense)
            self.add_emission(amount)
            return True
