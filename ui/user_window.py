import tkinter as tk
from tkinter import messagebox
from logic.data_handler import load_json_data, save_json_data
from PIL import Image, ImageTk

class UserApp:
    def __init__(self, root):
        self.root = root
        self.data = load_json_data()
        self.items = self.data["items"]
        # Центрируем окно и устанавливаем размер
        self.center_window(self.root, 800, 600)
        self.view_items()

    def view_items(self):
        # Создаем окно для просмотра лотов
        items_window = self.root
        items_window.title("Список лотов")

        # Центрируем окно и устанавливаем размер
        self.center_window(items_window, 800, 600)

        # Создаем Canvas и Scrollbar для прокрутки
        canvas = tk.Canvas(items_window)
        scrollbar = tk.Scrollbar(items_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Размещаем Scrollbar и Canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Создаем фрейм внутри canvas для размещения элементов
        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Строки для отображения
        self.item_labels = {}  # Словарь для хранения меток с лотами, чтобы обновлять цену

        for item in self.items:
            # Создаем строку для лота
            item_str = f"ID: {item['id']} | Название: {item['name']} | Описание: {item['description']} | Начальная цена: {item['starting_price']}"
            label = tk.Label(frame, text=item_str)
            label.pack()

            self.item_labels[item['id']] = label  # Сохраняем метку для обновления

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

            # Кнопка для того, чтобы делать ставку на лот
            tk.Button(frame, text="Сделать ставку", command=lambda i=item: self.place_bid(i)).pack(pady=5)

        # Добавляем кнопку "Выход"
        tk.Button(items_window, text="Выход", command=self.logout).pack(pady=10)

        # Обновляем область прокрутки
        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def place_bid(self, item):
        # Создаем окно для ввода ставки
        bid_window = tk.Toplevel(self.root)
        bid_window.title(f"Ставка на лот {item['id']}")

        # Центрируем окно и устанавливаем размер
        self.center_window(bid_window, 400, 250)

        tk.Label(bid_window, text="Введите сумму ставки:").pack(pady=5)
        self.bid_amount_entry = tk.Entry(bid_window)
        self.bid_amount_entry.pack(pady=5)

        # Кнопка для подтверждения ставки
        tk.Button(bid_window, text="Сделать ставку", command=lambda: self.confirm_bid(item, bid_window)).pack(pady=10)

    def confirm_bid(self, item, bid_window):
        bid_amount = self.bid_amount_entry.get()

        # Проверка на валидность ставки
        if not bid_amount.isdigit():
            messagebox.showerror("Ошибка", "Ставка должна быть числом.")
            return

        bid_amount = float(bid_amount)

        if bid_amount <= item["starting_price"]:
            messagebox.showerror("Ошибка", "Ставка должна быть больше начальной цены!")
            return

        # Если ставка валидна, обновляем данные
        item["starting_price"] = bid_amount  # Обновляем цену лота в данных

        # Обновляем отображаемую цену в интерфейсе
        item_label = self.item_labels.get(item["id"])  # Получаем метку для этого лота
        if item_label:
            # Обновляем текст с ценой
            item_label.config(text=f"ID: {item['id']} | Название: {item['name']} | Описание: {item['description']} | Начальная цена: {item['starting_price']}")

        # Сохраняем изменения в файл
        save_json_data(self.data)

        messagebox.showinfo("Успех", f"Вы успешно сделали ставку в размере {bid_amount} на лот {item['id']}.")
        bid_window.destroy()

    def center_window(self, window, width, height):
        # Центрируем окно на экране
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_left}+{position_top}')


    def logout(self):
        # Отложенный импорт
        from ui.main_window import LoginWindow

        self.root.destroy()
        login_window = tk.Tk()
        app = LoginWindow(login_window)
        login_window.mainloop()
