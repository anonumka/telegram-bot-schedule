import json

input_file = open('config.json')
settings = json.load(input_file)
input_file.close()


def write_config(data):
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
