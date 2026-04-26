import tkinter as tk
from tkinter import messagebox, ttk
import requests
import json
import os

# --- Константы ---
GITHUB_API_URL = "https://api.github.com/search/users"
FAVORITES_FILE = "favorites.json"

# --- Функции ---

def search_github_users():
    """
    Ищет пользователей GitHub по введенному имени.
    """
    query = search_entry.get().strip()
    if not query:
        messagebox.showwarning("Предупреждение", "Поле поиска не должно быть пустым.")
        return

    try:
        response = requests.get(GITHUB_API_URL, params={"q": query})
        response.raise_for_status()  # Вызовет исключение для плохих ответов (4xx или 5xx)
        data = response.json()
        users = data.get("items", [])
        display_search_results(users)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Ошибка при запросе к GitHub API: {e}")

def display_search_results(users):
    """
    Отображает результаты поиска в виде списка.
    """
    # Очистка предыдущих результатов
    for item in tree.get_children():
        tree.delete(item)

    for user in users:
        user_id = user["id"]
        login = user["login"]
        avatar_url = user.get("avatar_url", "No Avatar")
        tree.insert("", "end", values=(login, avatar_url), iid=user_id)

def add_to_favorites(event):
    """
    Добавляет выбранного пользователя в избранное.
    """
    selected_item = tree.selection()
    if not selected_item:
        return

    user_id = selected_item[0]
    user_login = tree.item(user_id, "values")[0]
    avatar_url = tree.item(user_id, "values")[1]

    favorites = load_favorites()
    if user_login not in favorites:
        favorites[user_login] = {"id": user_id, "avatar_url": avatar_url}
        save_favorites(favorites)
        messagebox.showinfo("Успех", f"Пользователь '{user_login}' добавлен в избранное.")
        update_favorites_list()
    else:
        messagebox.showinfo("Информация", f"Пользователь '{user_login}' уже в избранном.")

def load_favorites():
    """
    Загружает избранных пользователей из JSON файла.
    """
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_favorites(favorites):
    """
    Сохраняет избранных пользователей в JSON файл.
    """
    with open(FAVORITES_FILE, "w") as f:
        json.dump(favorites, f, indent=4)

def show_favorites():
    """
    Отображает список избранных пользователей.
    """
    favorites = load_favorites()
    if not favorites:
        messagebox.showinfo("Избранное", "Список избранных пользователей пуст.")
        return

    fav_window = tk.Toplevel(app)
    fav_window.title("Избранные пользователи")
    fav_window.geometry("300x400")

    fav_tree = ttk.Treeview(fav_window, columns=("Login", "Avatar URL"), show="headings")
    fav_tree.heading("Login", text="Пользователь")
    fav_tree.heading("Avatar URL", text="URL Аватара")
    fav_tree.pack(expand=True, fill="both")

    for login, data in favorites.items():
        fav_tree.insert("", "end", values=(login, data.get("avatar_url", "N/A")))

def update_favorites_list():
    """
    Обновляет отображение списка избранных (если окно открыто).
    """
    # В данной реализации обновление происходит при перезапуске или обновлении GUI
    pass

# --- GUI ---
app = tk.Tk()
app.title("GitHub User Finder")

# Поле ввода
search_frame = tk.Frame(app)
search_frame.pack(pady=10)

tk.Label(search_frame, text="Имя пользователя GitHub:").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, width=40)
search_entry.pack(side=tk.LEFT, padx=5)
search_button = tk.Button(search_frame, text="Найти", command=search_github_users)
search_button.pack(side=tk.LEFT)

# Результаты поиска (Treeview - для красивого отображения таблицы)
results_frame = tk.Frame(app)
results_frame.pack(pady=10, padx=10, fill="both", expand=True)

tree = ttk.Treeview(results_frame, columns=("Login", "Avatar URL"), show="headings")
tree.heading("Login", text="Пользователь")
tree.heading("Avatar URL", text="URL Аватара")
tree.column("Login", width=150)
tree.column("Avatar URL", width=200)
tree.pack(side=tk.LEFT, fill="both", expand=True)

scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill="y")

# Кнопка "Добавить в избранное"
add_fav_button = tk.Button(app, text="Добавить в избранное", command=lambda: add_to_favorites(None)) # Передаем None, чтобы не вызывать событие
add_fav_button.pack(pady=5)
tree.bind("<Double-1>", add_to_favorites) # Добавление по двойному клику

# Кнопка "Показать избранных"
show_fav_button = tk.Button(app, text="Показать избранных", command=show_favorites)
show_fav_button.pack(pady=5)

# --- Инициализация ---
# Загрузка избранных при запуске (для информации, но не для отображения в основном окне)
initial_favorites = load_favorites()

app.mainloop()
