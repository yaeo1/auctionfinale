import tkinter as tk
from tkinter import messagebox
from logic.data_handler import authenticate_user  # Импортируем функцию для аутентификации
from ui.admin_window import AdminApp
from ui.seller_window import SellerApp
from ui.user_window import UserApp


def center_window(window, width, height):
    # Центрируем окно на экране
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_left = int(screen_width / 2 - width / 2)
    window.geometry(f'{width}x{height}+{position_left}+{position_top}')


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Авторизация")

        # Центрируем окно
        center_window(self.root, 400, 250)

        self.greeting_widgets()
        self.current_user = None  # Сохраняем текущего пользователя

    def create_widgets(self):
        # Поля для ввода логина и пароля
        for widget in self.root.winfo_children():
            widget.destroy()
        tk.Label(self.root, text="Логин:").pack(pady=5)
        self.login_entry = tk.Entry(self.root)
        self.login_entry.pack(pady=5)

        tk.Label(self.root, text="Пароль:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)

        # Кнопки
        tk.Button(text="Войти", command=self.authenticate).pack(pady=10)

    def greeting_widgets(self):
        tk.Label(self.root, text="Аукцион", font=("Arial", 16)).pack(pady=5)
        tk.Button(text="Войти как продавец", command=self.create_widgets).pack(pady=10)
        tk.Button(text="Войти как покупатель", command=self.open_user_window).pack(pady=10)

    def authenticate(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        # Аутентификация пользователя
        user = authenticate_user(login, password)

        if user:
            self.current_user = user  # Сохраняем информацию о текущем пользователе
            if user["role"] == "admin":
                self.open_admin_window()
            elif user["role"] == "seller":
                self.open_seller_window(user)  # Передаем данные о текущем продавце
            else:
                messagebox.showerror("Ошибка", "Неизвестная роль пользователя!")
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def open_admin_window(self):
        self.root.destroy()
        admin_window = tk.Tk()
        app = AdminApp(admin_window)
        admin_window.mainloop()

    def open_seller_window(self, user):
        self.root.destroy()
        seller_window = tk.Tk()
        app = SellerApp(seller_window, user)  # Передаем данные о продавце
        seller_window.mainloop()

    def open_user_window(self):
        # Открыть окно обычного пользователя (гостя)
        self.root.destroy()
        user_window = tk.Tk()
        app = UserApp(user_window)
        user_window.mainloop()