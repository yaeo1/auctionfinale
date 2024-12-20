import tkinter as tk
import os
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from logic.data_handler import load_json_data, save_json_data


class SellerApp:
    def __init__(self, root, user):
        self.root = root  # Сохраняем данные о продавце
        self.user = user
        self.seller_id = self.user["id"]  # Используем ID продавца для фильтрации лотов
        self.center_window(self.root, 600, 400)
        self.create_widgets()


    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_left}+{position_top}')

    def get_seller_info(self):
        # Получаем информацию о продавце
        seller_id = 1  # Идентификатор продавца, например
        data = load_json_data()
        for seller in data["sellers"]:
            if seller["id"] == seller_id:
                return seller
        return None

    def create_widgets(self):
        tk.Label(self.root, text=f"Добро пожаловать!", font=("Arial", 16)).pack(pady=20)
        tk.Button(self.root, text="Просмотр моих лотов", command=self.view_my_items).pack(pady=5)
        tk.Button(self.root, text="Добавить новый лот", command=self.add_item_window).pack(pady=5)
        tk.Button(self.root, text="Редактировать лот", command=self.edit_item).pack(pady=5)
        tk.Button(self.root, text="Выйти", command=self.logout).pack(pady=20)

    def logout(self):
        from ui.main_window import LoginWindow
        self.root.destroy()
        login_window = tk.Tk()
        app = LoginWindow(login_window)
        login_window.mainloop()

    def view_my_items(self):
        # Загружаем данные из файла
        data = load_json_data()

        # Фильтруем лоты по seller_id (только те, которые принадлежат текущему продавцу)
        items = [item for item in data["items"] if item["seller_id"] == self.seller_id]

        if not items:
            messagebox.showinfo("Мои лоты", "У вас нет лотов.")
            return

        # Создаем окно для отображения лотов
        window = tk.Toplevel(self.root)
        window.title("Мои лоты")
        self.center_window(window, 600, 400)

        # Создаем Canvas и Scrollbar для прокрутки
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
        for item in items:
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

    def add_item_window(self):
        window = tk.Toplevel(self.root)
        window.title("Добавить новый лот")
        self.center_window(window, 400, 500)

        tk.Label(window, text="Название лота:").pack(pady=5)
        name_entry = tk.Entry(window)
        name_entry.pack(pady=5)

        tk.Label(window, text="Описание:").pack(pady=5)
        description_entry = tk.Entry(window)
        description_entry.pack(pady=5)

        tk.Label(window, text="Начальная цена:").pack(pady=5)
        starting_price_entry = tk.Entry(window)
        starting_price_entry.pack(pady=5)

        tk.Label(window, text="Фото (путь к файлу):").pack(pady=5)
        photo_entry = tk.Entry(window)
        photo_entry.pack(pady=5)

        def choose_photo():
            file_path = filedialog.askopenfilename(
                title="Выберите изображение",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")]
            )
            if file_path:
                photo_entry.config(state="normal")
                photo_entry.delete(0, tk.END)
                photo_entry.insert(0, file_path)
                photo_entry.config(state="readonly")

        tk.Button(window, text="Выбрать изображение", command=choose_photo).pack(pady=5)

        def add_item_action():
            name = name_entry.get()
            description = description_entry.get()
            try:
                starting_price = float(starting_price_entry.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную начальную цену!")
                return

            photo_path = photo_entry.get()

            if not photo_path:
                messagebox.showerror("Ошибка", "Выберите изображение!")
                return

            try:
                # Копируем изображение в папку ./img
                destination_folder = "./img"
                os.makedirs(destination_folder, exist_ok=True)
                destination_path = os.path.join(destination_folder, os.path.basename(photo_path))
                with open(photo_path, 'rb') as src_file:
                    with open(destination_path, 'wb') as dest_file:
                        dest_file.write(src_file.read())
                photo_path = destination_path  # Обновляем путь
            except FileNotFoundError:
                messagebox.showerror("Ошибка", "Файл изображения не найден!")
                return
            except PermissionError:
                messagebox.showerror("Ошибка", "Недостаточно прав для копирования файла!")
                return
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обработать изображение: {e}")
                return

            data = load_json_data()
            new_id = max([item["id"] for item in data["items"]], default=0) + 1
            new_item = {
                "id": new_id,
                "name": name,
                "description": description,
                "starting_price": starting_price,
                "photo": photo_path,  # Путь к картинке
                "seller_id": self.user["id"]
            }

            data["items"].append(new_item)
            save_json_data(data)
            messagebox.showinfo("Успех", "Лот добавлен!")
            window.destroy()

        tk.Button(window, text="Добавить", command=add_item_action).pack(pady=20)

    def edit_item(self):
        # Создаем новое окно для редактирования лота
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Редактировать лот")
        self.center_window(edit_window, 400, 300)

        # Метки и поля ввода
        tk.Label(edit_window, text="Введите ID лота для редактирования:").pack(pady=5)
        self.item_id_entry = tk.Entry(edit_window)
        self.item_id_entry.pack(pady=5)

        tk.Button(edit_window, text="Загрузить лот", command=self.load_item_data).pack(pady=10)

        # Поля для редактирования
        self.item_name_entry = tk.Entry(edit_window)
        self.item_name_entry.pack(pady=5)

        self.item_description_entry = tk.Entry(edit_window)
        self.item_description_entry.pack(pady=5)

        self.starting_price_entry = tk.Entry(edit_window)
        self.starting_price_entry.pack(pady=5)

        self.item_photo_path = None  # Здесь можно добавить фото, если нужно

        tk.Button(edit_window, text="Сохранить изменения", command=self.save_item_changes).pack(pady=10)

    def load_item_data(self):
        # Загружаем все лоты из данных
        data = load_json_data()
        item_id = self.item_id_entry.get()

        # Ищем лот с данным ID
        item = next((i for i in data["items"] if i["id"] == int(item_id) and i["seller_id"] == self.seller["id"]), None)

        if item:
            # Если лот найден, заполняем поля редактирования
            self.item_name_entry.delete(0, tk.END)
            self.item_name_entry.insert(0, item["name"])

            self.item_description_entry.delete(0, tk.END)
            self.item_description_entry.insert(0, item["description"])

            self.starting_price_entry.delete(0, tk.END)
            self.starting_price_entry.insert(0, item["starting_price"])

            # Заполнить поле для фото, если оно есть (если нужно)
            self.item_photo_path = item["photo"]
        else:
            messagebox.showerror("Ошибка", "Лот с таким ID не найден или не принадлежит вам.")

    def save_item_changes(self):
        # Получаем новые данные для лота
        item_id = self.item_id_entry.get()
        item_name = self.item_name_entry.get()
        item_description = self.item_description_entry.get()
        starting_price = float(self.starting_price_entry.get())

        # Загружаем текущие данные
        data = load_json_data()
        item = next((i for i in data["items"] if i["id"] == int(item_id) and i["seller_id"] == self.user["id"]), None)

        if item:
            # Обновляем данные лота
            item["name"] = item_name
            item["description"] = item_description
            item["starting_price"] = starting_price
            # Фото можно обновить, если нужно (если добавляем функционал с загрузкой фото)

            # Сохраняем обновленные данные в JSON
            save_json_data(data)

            messagebox.showinfo("Успех", "Лот успешно обновлен!")
        else:
            messagebox.showerror("Ошибка", "Лот с таким ID не найден или не принадлежит вам.")

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_left = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_left}+{position_top}')