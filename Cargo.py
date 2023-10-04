from enum import Enum


class Cargo_Types(Enum):
    WOOD = 1
    METAL = 2


class Cargo:
    def __init__(self, cargo_type, name, weight, size, price, description, dest=None):
        # using cargo_type instead of type, because type is a built-in name
        self.name = name
        self.cargo_type = cargo_type
        self.weight = weight
        self.size = size
        self.dest = dest
        self.price = price
        self.description = description

    @staticmethod
    def load_all_cargo_metadata(json_data):
        all_cargo_metadata_dict = json_data.get("cargos", [])
        all_cargo_metadata_enum = {}
        for cargo_name in all_cargo_metadata_dict:
            cargo_name_enum = Cargo_Types[cargo_name.upper()]
            attributes = {
                "name": cargo_name,
                "price": all_cargo_metadata_dict[cargo_name]["price"],
                "weight": all_cargo_metadata_dict[cargo_name]["weight"],
                "size": all_cargo_metadata_dict[cargo_name]["size"],
                "description": all_cargo_metadata_dict[cargo_name]["description"],
            }
            all_cargo_metadata_enum[cargo_name_enum] = attributes
        return all_cargo_metadata_enum

    @staticmethod
    def create_cargo(cargo_type: Cargo_Types, all_cargo_metadata: dict, dest: str):
        # weight = data
        return Cargo(cargo_type,
                     all_cargo_metadata[cargo_type]["name"],
                     all_cargo_metadata[cargo_type]["weight"],
                     all_cargo_metadata[cargo_type]["size"],
                     all_cargo_metadata[cargo_type]["price"],
                     all_cargo_metadata[cargo_type]["description"],
                     dest)
