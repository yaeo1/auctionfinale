import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from tkinter import filedialog
from PIL import Image, ImageTk
from io import BytesIO
import requests
from logic.data_handler import load_json_data, save_json_data

class AdminApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Администратор")

        # Центрируем окно
        self.center_window(self.root, 600, 400)

        self.create_widgets()

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_left}+{position_top}')

    def create_widgets(self):
        tk.Label(self.root, text="Добро пожаловать, Администратор!", font=("Arial", 16)).pack(pady=20)

        # Кнопки для функционала администратора
        tk.Button(self.root, text="Просмотр всех пользователей", command=self.view_users).pack(pady=5)
        tk.Button(self.root, text="Просмотр всех продавцов", command=self.view_sellers).pack(pady=5)
        tk.Button(self.root, text="Просмотр всех лотов", command=self.view_items).pack(pady=5)
        tk.Button(self.root, text="Добавить нового пользователя", command=self.add_user_window).pack(pady=5)
        tk.Button(self.root, text="Добавить нового продавца", command=self.add_seller_window).pack(pady=5)
        tk.Button(self.root, text="Добавить новый лот", command=self.add_item_window).pack(pady=5)
        tk.Button(self.root, text="Экспортировать данные в Excel", command=self.export_to_excel).pack(pady=5)
        tk.Button(self.root, text="Выйти", command=self.logout).pack(pady=20)

    def logout(self):
        # Отложенный импорт
        from ui.main_window import LoginWindow

        self.root.destroy()
        login_window = tk.Tk()
        app = LoginWindow(login_window)
        login_window.mainloop()

    def view_users(self):
        data = load_json_data()
        users = data["users"]

        if not users:
            messagebox.showinfo("Список пользователей", "Нет пользователей.")
            return

        max_login_length = max(len(user["login"]) for user in users) if users else 10
        max_role_length = max(len(user["role"]) for user in users) if users else 10
        window_width = max(600, max_login_length * 10, max_role_length * 10)

        window = tk.Toplevel(self.root)
        window.title("Список пользователей")
        self.center_window(window, window_width, 400)

        tree = ttk.Treeview(window, columns=("ID", "Логин", "Роль"), show="headings")
        tree.heading("ID", text="ID", command=lambda: self.sort_column(tree, users, "ID", False))
        tree.heading("Логин", text="Логин")
        tree.heading("Роль", text="Роль")
        tree.pack(fill="both", expand=True)

        for user in users:
            tree.insert("", "end", values=(user["id"], user["login"], user["role"]))

        close_button = tk.Button(window, text="Закрыть", command=window.destroy)
        close_button.pack(pady=10)

    def sort_column(self, tree, data, col, reverse):
        # Сортируем данные по ключу
        data.sort(key=lambda x: x[col.lower()], reverse=reverse)  # Используем ключ с малой буквы для сортировки

        # Очищаем таблицу
        for row in tree.get_children():
            tree.delete(row)

        # Перезаполняем таблицу отсортированными данными
        for user in data:
            tree.insert("", "end", values=(user["id"], user["login"], user["role"]))

        # Меняем направление сортировки
        tree.heading(col, command=lambda: self.sort_column(tree, data, col, not reverse))

    def view_sellers(self):
        data = load_json_data()
        sellers = data["sellers"]

        if not sellers:
            messagebox.showinfo("Список продавцов", "Нет продавцов.")
            return

        # Получаем максимальную длину данных в каждом столбце для расчета ширины окна
        max_name_length = max(len(seller["first_name"]) for seller in sellers) if sellers else 10
        max_last_name_length = max(len(seller["last_name"]) for seller in sellers) if sellers else 10
        max_phone_length = max(len(seller["phone"]) for seller in sellers) if sellers else 10

        # Ширина окна будет зависеть от самой длинной строки в каждом столбце
        window_width = max(1000, max_name_length * 10, max_last_name_length * 10, max_phone_length * 10)

        window = tk.Toplevel(self.root)
        window.title("Список продавцов")
        self.center_window(window, window_width, 400)  # Центрируем окно

        # Создаем таблицу
        tree = ttk.Treeview(window, columns=("ID", "Имя", "Фамилия", "Телефон", "ID пользователя"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Имя", text="Имя")
        tree.heading("Фамилия", text="Фамилия")
        tree.heading("Телефон", text="Телефон")
        tree.heading("ID пользователя", text="ID пользователя")
        tree.pack(fill="both", expand=True)

        # Добавляем данные продавцов в таблицу
        for seller in sellers:
            tree.insert("", "end", values=(
                seller["id"], seller["first_name"], seller["last_name"], seller["phone"], seller["user_id"]))

        # Добавляем кнопку "Закрыть" для выхода
        close_button = tk.Button(window, text="Закрыть", command=window.destroy)
        close_button.pack(pady=10)

    def view_items(self):
        # Загружаем данные из файла
        data = load_json_data()

        # Создаем окно для отображения лотов
        window = tk.Toplevel(self.root)
        window.title("Список лотов")

        self.center_window(window, 600, 400)

        # Создаем Canvas и Scrollbar
        canvas = tk.Canvas(window)
        scrollbar = tk.Scrollbar(window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Размещаем Scrollbar и Canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Создаем фрейм внутри canvas
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Строки для отображения лотов
        for item in data["items"]:
            # Создаем строку для лота
            item_str = f"ID: {item['id']} | Название: {item['name']} | Описание: {item['description']} | Начальная цена: {item['starting_price']}"

            # Показываем информацию о лоте
            label = tk.Label(frame, text=item_str)
            label.pack()

            # Загружаем картинку, если она есть
            if item['photo']:
                try:
                    # Попытка загрузить картинку
                    image = Image.open(item['photo'])
                    image = image.resize((100, 100))  # Устанавливаем размер картинки
                    photo = ImageTk.PhotoImage(image)

                    # Показываем картинку
                    image_label = tk.Label(frame, image=photo)
                    image_label.photo = photo  # Сохраняем ссылку на объект изображения
                    image_label.pack()

                except Exception as e:
                    # Если не удалось загрузить картинку, показываем ошибку
                    messagebox.showerror("Ошибка", f"Не удалось загрузить картинку: {e}")

        # Обновляем область прокрутки
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # Кнопка для закрытия окна
        tk.Button(window, text="Закрыть", command=window.destroy).pack(pady=10)

    def load_image_from_url(self, url):
        """Загружает изображение по URL и возвращает его как объект Tkinter"""
        try:
            # Загружаем изображение по URL
            response = requests.get(url)
            img_data = response.content
            img = Image.open(BytesIO(img_data))

            # Преобразуем изображение в формат, совместимый с Tkinter
            img = img.resize((100, 100))  # Устанавливаем размер изображения (по необходимости)
            img_tk = ImageTk.PhotoImage(img)

            return img_tk
        except Exception as e:
            print(f"Error loading image from URL {url}: {e}")
            return None
    def add_user_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить нового пользователя")
        window.geometry("300x250")
        self.center_window(window, 300, 250)

        tk.Label(window, text="Логин:").pack(pady=5)
        login_entry = tk.Entry(window)
        login_entry.pack(pady=5)

        tk.Label(window, text="Пароль:").pack(pady=5)
        password_entry = tk.Entry(window, show="*")
        password_entry.pack(pady=5)

        tk.Label(window, text="Роль (admin/seller):").pack(pady=5)
        role_entry = tk.Entry(window)
        role_entry.pack(pady=5)

        def add_user_action():
            login = login_entry.get()
            password = password_entry.get()
            role = role_entry.get().lower()

            if role not in ["admin", "seller"]:
                messagebox.showerror("Ошибка", "Неверная роль!")
                return

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
            messagebox.showinfo("Успех", "Пользователь добавлен!")
            window.destroy()

        tk.Button(window, text="Добавить", command=add_user_action).pack(pady=20)

    def add_seller_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить нового продавца")
        window.geometry("300x300")
        self.center_window(window, 300, 300)

        tk.Label(window, text="Имя:").pack(pady=5)
        first_name_entry = tk.Entry(window)
        first_name_entry.pack(pady=5)

        tk.Label(window, text="Фамилия:").pack(pady=5)
        last_name_entry = tk.Entry(window)
        last_name_entry.pack(pady=5)

        tk.Label(window, text="Телефон:").pack(pady=5)
        phone_entry = tk.Entry(window)
        phone_entry.pack(pady=5)

        tk.Label(window, text="ID пользователя:").pack(pady=5)
        user_id_entry = tk.Entry(window)
        user_id_entry.pack(pady=5)

        def add_seller_action():
            first_name = first_name_entry.get()
            last_name = last_name_entry.get()
            phone = phone_entry.get()
            user_id = user_id_entry.get()

            try:
                user_id = int(user_id)
            except ValueError:
                messagebox.showerror("Ошибка", "ID пользователя должно быть числом!")
                return

            data = load_json_data()

            if not any(user["id"] == user_id for user in data["users"]):
                messagebox.showerror("Ошибка", "Пользователь с таким ID не найден!")
                return

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
            messagebox.showinfo("Успех", "Продавец добавлен!")
            window.destroy()

        tk.Button(window, text="Добавить", command=add_seller_action).pack(pady=20)

    def add_item_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить новый лот")
        window.geometry("300x300")
        self.center_window(window, 300, 300)

        tk.Label(window, text="Название лота:").pack(pady=5)
        name_entry = tk.Entry(window)
        name_entry.pack(pady=5)

        tk.Label(window, text="Описание:").pack(pady=5)
        description_entry = tk.Entry(window)
        description_entry.pack(pady=5)

        tk.Label(window, text="Начальная цена:").pack(pady=5)
        starting_price_entry = tk.Entry(window)
        starting_price_entry.pack(pady=5)

        tk.Label(window, text="Фото (URL):").pack(pady=5)
        photo_entry = tk.Entry(window)
        photo_entry.pack(pady=5)

        def add_item_action():
            name = name_entry.get()
            description = description_entry.get()
            try:
                starting_price = int(starting_price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную начальную цену!")
                return
            photo = photo_entry.get()

            data = load_json_data()
            new_id = max([item["id"] for item in data["items"]], default=0) + 1
            new_item = {
                "id": new_id,
                "name": name,
                "description": description,
                "starting_price": starting_price,
                "photo": photo,
                "seller_id": 1  # Можете добавить динамическое назначение seller_id
            }

            data["items"].append(new_item)
            save_json_data(data)
            messagebox.showinfo("Успех", "Лот добавлен!")
            window.destroy()

        tk.Button(window, text="Добавить", command=add_item_action).pack(pady=20)

    def export_to_excel(self):
        # Загружаем данные
        data = load_json_data()

        # Создаем DataFrames для пользователей, продавцов и лотов
        users_df = pd.DataFrame(data["users"])
        sellers_df = pd.DataFrame(data["sellers"])
        items_df = pd.DataFrame(data["items"])

        # Открываем диалоговое окно для выбора пути сохранения файла
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            # Создаем ExcelWriter и записываем все три DataFrame в отдельные листы
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                users_df.to_excel(writer, index=False, sheet_name="Users")
                sellers_df.to_excel(writer, index=False, sheet_name="Sellers")
                items_df.to_excel(writer, index=False, sheet_name="Items")

            messagebox.showinfo("Экспорт завершен", f"Данные успешно экспортированы в файл: {file_path}")
        else:
            messagebox.showerror("Ошибка", "Не был выбран файл для сохранения.")
