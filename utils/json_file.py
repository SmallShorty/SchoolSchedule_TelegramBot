import json

def load_data(file_path):
    with open(file_path, 'r') as file:
        schedule = json.load(file)
    return schedule

def save_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
