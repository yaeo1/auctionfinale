import json
import os

DATA_FILE = "database/data.json"

def load_json_data():
    if not os.path.exists(DATA_FILE):
        return {"users": [], "sellers": [], "items": []}
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def authenticate_user(login, password):
    # Загружаем данные пользователей и продавцов
    data = load_json_data()
    users = data["users"]

    # Поиск пользователя по логину и паролю
    for user in users:
        if user["login"] == login and user["password"] == password:
            return user
    return None
