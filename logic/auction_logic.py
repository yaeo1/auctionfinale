from logic.data_handler import load_json_data, save_json_data

# Функции для работы с пользователями
def create_user(login, password, role):
    data = load_json_data()
    new_id = max([user["id"] for user in data["users"]], default=0) + 1
    new_user = {
        "id": new_id,
        "login": login,
        "password": password,
        "role": role
    }
    data["users"].append(new_user)
    save_json_data(data)

def get_user_by_login(login):
    data = load_json_data()
    for user in data["users"]:
        if user["login"] == login:
            return user
    return None

# Функции для работы с продавцами
def create_seller(first_name, last_name, phone, user_id):
    data = load_json_data()
    new_id = max([seller["id"] for seller in data["sellers"]], default=0) + 1
    new_seller = {
        "id": new_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "user_id": user_id
    }
    data["sellers"].append(new_seller)
    save_json_data(data)

def get_seller_by_user_id(user_id):
    data = load_json_data()
    for seller in data["sellers"]:
        if seller["user_id"] == user_id:
            return seller
    return None

# Функции для работы с лотами
def create_item(name, description, starting_price, photo, seller_id):
    data = load_json_data()
    # Проверяем, существует ли продавец с таким seller_id
    if not any(seller["id"] == seller_id for seller in data["sellers"]):
        raise ValueError(f"Продавец с ID {seller_id} не найден.")

    new_id = max([item["id"] for item in data["items"]], default=0) + 1
    new_item = {
        "id": new_id,
        "name": name,
        "description": description,
        "starting_price": starting_price,
        "photo": photo,
        "seller_id": seller_id
    }
    data["items"].append(new_item)
    save_json_data(data)

def get_items_by_seller(seller_id):
    data = load_json_data()
    return [item for item in data["items"] if item["seller_id"] == seller_id]

# Функции для аутентификации
def authenticate_user(login, password):
    user = get_user_by_login(login)
    if user and user["password"] == password:
        return user
    return None
