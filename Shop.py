from enum import Enum


class Shop_Item(Enum):
    FUEL = 1
    EMISSION = 2


class Shop_Item_Detail:
    def __init__(self, price, unit, description):
        self.price = price
        self.unit = unit
        self.description = description


class Shop:
    def __init__(self, shop_items, unavailable_items=None):
        # todo feature: different city has different shop
        # todo feature: some shops does not have all items
        self.shop_items = shop_items

    @staticmethod
    def load_all_shop_metadata(json_data):
        all_shop_metadata_dict = json_data.get("shop_items", [])
        all_shop_metadata_enum = {}
        for item_name in all_shop_metadata_dict:
            item_enum = Shop_Item[item_name.upper()]  # Shop_Items is enum
            item = Shop_Item_Detail(all_shop_metadata_dict[item_name]["price"],
                                    all_shop_metadata_dict[item_name]["unit"],
                                    all_shop_metadata_dict[item_name]["description"])
            all_shop_metadata_enum[item_enum] = item
        return all_shop_metadata_enum

    @staticmethod
    def create_shop(shop_items: Shop_Item_Detail, unavailable_items: list = None):
        """
        :param unavailable_items: A list of Shop_Item Enum that not available. Default: all items available.
        :return:
        """
        return Shop(shop_items)

    def buy(self, player, item: Shop_Item, amount):
        expense = self.shop_items[item].price * amount
        if expense > player.money:
            return False
        else:
            player.money -= expense

            # for basic: fuel and emission
            if item == Shop_Item.FUEL:
                player.fuel += amount
            elif item == Shop_Item.EMISSION:
                player.emission += amount

            # for other items (that may change in json file)
            else:
                print("Buying other items, yet not defined")
            return True
