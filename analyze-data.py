import json
import sys


def print_json_structure(data, indent=0):
    indent_str = " " * indent
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"\n{indent_str}{key}:", end="")
            print_json_structure(value, indent + 2)
    elif isinstance(data, list):
        print(f"{indent_str}List with {len(data)} items")
        if len(data) > 0:
            print_json_structure(data[0], indent + 2)
    else:
        print(f" {type(data).__name__}", end="")


with open(sys.argv[1], "r", encoding="utf-8") as file:
    data = json.load(file)
    print_json_structure(data)
