import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- Папка для хранения данных ---
APPDATA_DIR = os.path.join(os.environ["APPDATA"], "PNXTool")
os.makedirs(APPDATA_DIR, exist_ok=True)

LAST_VALUES_FILE = os.path.join(APPDATA_DIR, "last_values.json")
RULES_FILE = os.path.join(APPDATA_DIR, "rules.json")
REPLACE_RULES_FILE = os.path.join(APPDATA_DIR, "replace_rules.json")


# --- Работа с последними значениями для объединения ---
def load_last_values():
    if os.path.exists(LAST_VALUES_FILE):
        with open(LAST_VALUES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"folder": "", "search": "cutlist_", "ext": ".pnx"}


def save_last_values(folder, search, ext):
    with open(LAST_VALUES_FILE, "w", encoding="utf-8") as f:
        json.dump({"folder": folder, "search": search, "ext": ext}, f, ensure_ascii=False, indent=4)


# --- Работа с правилами разделения ---
def load_rules():
    if os.path.exists(RULES_FILE):
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "тим": ["тимбер", "вуд", "лдсп"],
            "без тим": ["синкрон", "пост"],
            "agt": ["evosoft", "evogloss", "agt"]
        }


def save_rules(rules):
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=4)
    messagebox.showinfo("Сохранено", f"Правила сохранены в {RULES_FILE}")


# ---------------------------
# Вкладка 1: Объединение
# ---------------------------
def create_combine_tab(notebook):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Объединение")

    folder_path = tk.StringVar()
    last = load_last_values()
    folder_path.set(last["folder"])

    # Папка
    tk.Label(tab, text="Папка с файлами:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
    tk.Entry(tab, textvariable=folder_path, width=50).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(tab, text="Обзор", command=lambda: folder_path.set(filedialog.askdirectory())).grid(
        row=0, column=2, padx=5, pady=5
    )

    # Строка поиска
    tk.Label(tab, text="Строка для поиска:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
    search_entry = tk.Entry(tab, width=50)
    search_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)
    search_entry.insert(0, last["search"])

    # Расширение файлов
    tk.Label(tab, text="Расширение файлов (например, .pnx):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
    file_ext_entry = tk.Entry(tab, width=10)
    file_ext_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)
    file_ext_entry.insert(0, last["ext"])

    def on_combine():
        if not folder_path.get() or not search_entry.get() or not file_ext_entry.get():
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return
        from combine import combine_files
        combine_files(folder_path.get(), search_entry.get(), file_ext_entry.get())
        save_last_values(folder_path.get(), search_entry.get(), file_ext_entry.get())

    tk.Button(tab, text="Объединить файлы", command=on_combine).grid(row=3, column=0, columnspan=3, pady=10)


# ---------------------------
# Вкладка 2: Разделение
# ---------------------------
def create_split_tab(notebook):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Разделение")

    DEFAULT_RULES = {
        "тим": ["тимбер", "вуд", "лдсп"],
        "без тим": ["синкрон", "пост"],
        "agt": ["evosoft", "evogloss", "agt"]
    }

    rules = load_rules()

    rules_text = tk.Text(tab, width=60, height=15, state=tk.NORMAL)
    rules_text.pack(padx=10, pady=10)

    def load_rules_to_text(rules_dict):
        rules_text.config(state=tk.NORMAL)
        rules_text.delete("1.0", tk.END)
        for cat, keywords in rules_dict.items():
            rules_text.insert(tk.END, f"{cat}: {', '.join(keywords)}\n")
        rules_text.config(state=tk.DISABLED)

    load_rules_to_text(rules)

    # Кнопки управления
    btn_frame = tk.Frame(tab)
    btn_frame.pack(pady=5, fill="x")

    def edit_rules():
        rules_text.config(state=tk.NORMAL)

    def save_rules_button():
        try:
            new_rules = {}
            lines = rules_text.get("1.0", tk.END).strip().split("\n")
            for line in lines:
                if ":" in line:
                    cat, kws = line.split(":", 1)
                    keywords = [k.strip() for k in kws.split(",") if k.strip()]
                    new_rules[cat.strip()] = keywords
            save_rules(new_rules)
            rules_text.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить правила:\n{e}")

    def restore_defaults():
        load_rules_to_text(DEFAULT_RULES)
        save_rules(DEFAULT_RULES)
        messagebox.showinfo("Восстановлено", "Стандартные настройки восстановлены.")

    def on_split():
        from split import split_file
        split_file()

    tk.Button(btn_frame, text="Изменить", command=edit_rules).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Сохранить", command=save_rules_button).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Восстановить стандартные", command=restore_defaults).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Разделить файл", command=on_split).pack(side=tk.RIGHT, padx=10)


# ---------------------------
# Вкладка 3: Замена текста
# ---------------------------
def create_replace_tab(notebook, root):
    import tkinter as tk
    from tkinter import ttk, filedialog
    from replace import load_replace_rules, save_replace_rules, apply_replacements_to_files, DEFAULT_REPLACE_RULES_FILE

    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Замена текста")

    replace_rules = load_replace_rules(DEFAULT_REPLACE_RULES_FILE)

    columns = ("old", "new")
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
    tree.heading("old", text="Что заменить")
    tree.heading("new", text="На что заменить")
    tree.pack(padx=10, pady=10, fill="both", expand=True)

    # --- заполняем таблицу ---
    for r in replace_rules:
        tree.insert("", tk.END, values=(r["old"], r["new"]))

    # --- кнопки управления ---
    btn_frame = tk.Frame(tab)
    btn_frame.pack(pady=5, fill="x")

    # --- Добавление ---
    def add_rule():
        add_window = tk.Toplevel(root)
        add_window.title("Добавить замену")
        tk.Label(add_window, text="Что заменить:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(add_window, text="На что заменить:").grid(row=1, column=0, padx=5, pady=5)
        old_entry = tk.Entry(add_window, width=50)
        old_entry.grid(row=0, column=1, padx=5, pady=5)
        new_entry = tk.Entry(add_window, width=50)
        new_entry.grid(row=1, column=1, padx=5, pady=5)

        def save_new():
            old = old_entry.get().strip()
            new = new_entry.get().strip()
            if not old:
                messagebox.showwarning("Ошибка", "Поле 'Что заменить' не может быть пустым!")
                return
            tree.insert("", tk.END, values=(old, new))
            add_window.destroy()

        tk.Button(add_window, text="Добавить", command=save_new).grid(row=2, column=0, columnspan=2, pady=10)

    # --- Удаление выбранных ---
    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Выберите хотя бы одну строку для удаления.")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить {len(selected)} правил?"):
            for item in selected:
                tree.delete(item)
            messagebox.showinfo("Готово", "Выбранные правила удалены.")

    # --- Сохранение ---
    def save_all_rules():
        rules_list = [
            {"old": tree.item(i, "values")[0], "new": tree.item(i, "values")[1]}
            for i in tree.get_children()
        ]
        save_replace_rules(rules_list, DEFAULT_REPLACE_RULES_FILE)
        messagebox.showinfo("Сохранено", "Правила успешно сохранены.")

    # --- Применение ---
    def apply_replacement():
        rules_list = [
            {"old": tree.item(i, "values")[0], "new": tree.item(i, "values")[1]}
            for i in tree.get_children()
        ]

        file_paths = filedialog.askopenfilenames(
            title="Выберите файлы для замены",
            filetypes=[("PNX файлы", "*.pnx"), ("Все файлы", "*.*")]
        )
        if not file_paths:
            return

        log_window = tk.Toplevel(root)
        log_window.title("Лог изменений")
        log_text = tk.Text(log_window, width=100, height=30)
        log_text.pack(padx=10, pady=10, fill="both", expand=True)

        apply_replacements_to_files(rules_list, file_paths, log_text_widget=log_text)

    # --- Кнопки ---
    tk.Button(btn_frame, text="Добавить", command=add_rule).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Удалить выбранное", command=delete_selected).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Сохранить правила", command=save_all_rules).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Применить замену", command=apply_replacement).pack(side=tk.RIGHT, padx=5)

# ---------------------------
# Вкладка 4: Добавление даты
# ---------------------------
def create_add_date_tab(notebook, root):
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    from add_date import append_date_to_files

    tab = ttk.Frame(notebook)
    notebook.add(tab, text="Добавить дату")

    mode_var = tk.StringVar(value="from_filename")  # from_filename | manual
    manual_date_var = tk.StringVar(value="2025-12-19")

    # --- выбор режима ---
    mode_frame = tk.LabelFrame(tab, text="Источник даты")
    mode_frame.pack(fill="x", padx=10, pady=10)

    rb1 = tk.Radiobutton(mode_frame, text="Взять дату из имени файла (YYYY-MM-DD)", variable=mode_var, value="from_filename")
    rb1.pack(anchor="w", padx=10, pady=3)

    rb2 = tk.Radiobutton(mode_frame, text="Ввести дату вручную (YYYY-MM-DD)", variable=mode_var, value="manual")
    rb2.pack(anchor="w", padx=10, pady=3)

    # --- ввод даты вручную ---
    manual_frame = tk.Frame(tab)
    manual_frame.pack(fill="x", padx=10, pady=(0, 10))

    tk.Label(manual_frame, text="Дата:").pack(side=tk.LEFT)
    manual_entry = tk.Entry(manual_frame, textvariable=manual_date_var, width=15)
    manual_entry.pack(side=tk.LEFT, padx=8)

    def refresh_manual_state(*_):
        state = tk.NORMAL if mode_var.get() == "manual" else tk.DISABLED
        manual_entry.config(state=state)

    mode_var.trace_add("write", refresh_manual_state)
    refresh_manual_state()

    # --- кнопка запуска ---
    def run():
        file_paths = filedialog.askopenfilenames(
            title="Выберите файлы для добавления даты",
            filetypes=[("PNX файлы", "*.pnx"), ("Все файлы", "*.*")]
        )
        if not file_paths:
            return

        log_window = tk.Toplevel(root)
        log_window.title("Лог добавления даты")
        log_text = tk.Text(log_window, width=100, height=30)
        log_text.pack(padx=10, pady=10, fill="both", expand=True)

        append_date_to_files(
            file_paths=file_paths,
            mode=mode_var.get(),
            manual_date=manual_date_var.get(),
            log_text_widget=log_text
        )

    tk.Button(tab, text="Выбрать файлы и добавить дату", command=run).pack(padx=10, pady=10, anchor="e")


# ---------------------------
# Запуск GUI
# ---------------------------
def main():
    root = tk.Tk()
    root.title("PNX Tool")
    root.resizable(False, False)  # запрет изменения размера

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    create_combine_tab(notebook)
    create_split_tab(notebook)
    create_replace_tab(notebook, root)
    create_add_date_tab(notebook, root)  # <-- добавили

    root.mainloop()



if __name__ == "__main__":
    main()
