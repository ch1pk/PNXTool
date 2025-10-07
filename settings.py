import json
import os
import tkinter as tk
from tkinter import simpledialog, messagebox

RULES_FILE = "rules.json"  # файл для хранения категорий

def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        # пример стандартных категорий
        return {
            "тимбер": ["тимбер", "вуд", "лдсп"],
            "без тим": ["синкрон", "пост"],
            "agt": ["evosoft", "evogloss", "agt"]
        }

def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=4, ensure_ascii=False)

def show_rules():
    rules = load_rules()
    text_widget.delete("1.0", tk.END)
    for cat, keywords in rules.items():
        text_widget.insert(tk.END, f"{cat}: {', '.join(keywords)}\n")

def add_category():
    rules = load_rules()
    cat = simpledialog.askstring("Добавить категорию", "Введите название категории:")
    if cat:
        if cat in rules:
            messagebox.showwarning("Внимание", "Такая категория уже существует!")
            return
        rules[cat] = []
        save_rules(rules)
        show_rules()

def remove_category():
    rules = load_rules()
    cat = simpledialog.askstring("Удалить категорию", "Введите название категории для удаления:")
    if cat in rules:
        del rules[cat]
        save_rules(rules)
        show_rules()
    else:
        messagebox.showwarning("Ошибка", "Такой категории нет!")

def edit_category():
    rules = load_rules()
    cat = simpledialog.askstring("Изменить категорию", "Введите название категории для редактирования:")
    if cat in rules:
        keywords = simpledialog.askstring("Ключевые слова", "Введите ключевые слова через запятую:",
                                          initialvalue=",".join(rules[cat]))
        if keywords is not None:
            rules[cat] = [k.strip() for k in keywords.split(",") if k.strip()]
            save_rules(rules)
            show_rules()
    else:
        messagebox.showwarning("Ошибка", "Такой категории нет!")

# --- GUI вкладки Настройки ---
def create_settings_tab(notebook):
    tab_settings = tk.Frame(notebook)
    notebook.add(tab_settings, text="Настройки")

    global text_widget
    text_widget = tk.Text(tab_settings, width=50, height=15)
    text_widget.pack(pady=10)

    btn_frame = tk.Frame(tab_settings)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Добавить категорию", command=add_category).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Изменить категорию", command=edit_category).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Удалить категорию", command=remove_category).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Обновить список", command=show_rules).grid(row=0, column=3, padx=5)

    show_rules()  # показываем текущие правила при открытии вкладки
