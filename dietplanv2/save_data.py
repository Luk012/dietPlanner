import json
import sys

def save_data(data):
    with open('user_data.json', 'w') as file:
        json.dump(data, file)

if __name__ == '__main__':
    data = json.load(sys.stdin)
    save_data(data)
