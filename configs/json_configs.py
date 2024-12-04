import json

def load_json_data(file_path):
    """
    Loads the JSON data from the given file path.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except FileNotFoundError as e:
# sourcery skip: raise-specific-error
        raise Exception(f"The file {file_path} was not found.") from e
    except json.JSONDecodeError as e:
# sourcery skip: raise-specific-error
        raise Exception(f"The file {file_path} is not a valid JSON file.") from e