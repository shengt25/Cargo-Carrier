def load_metadata(json_file):
    with open(json_file, 'r') as file:
        json_data = json.load(file)
        return json_data