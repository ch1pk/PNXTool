import os
from tkinter import messagebox
from utils import read_file_safely

def combine_files(folder, search_text, file_ext):
    if not folder or not search_text or not file_ext:
        messagebox.showwarning("Ошибка", "Заполните все поля!")
        return

    all_files = [f for f in os.listdir(folder) if f.endswith(file_ext) and search_text in f]

    if not all_files:
        messagebox.showinfo("Результат", "Файлы не найдены.")
        return

    combined_content = ""
    for file_name in all_files:
        file_path = os.path.join(folder, file_name)
        content = read_file_safely(file_path)
        # Разбиваем на строки и убираем пустые в конце
        lines = content.rstrip("\n").splitlines()
        combined_content += "\n".join(lines) + "\n"  # добавляем ровно один перенос между файлами

    # сохраняем только в cp1251
    output_file = os.path.join(folder, f"объединено_{search_text.replace(' ', '_')}{file_ext}")
    with open(output_file, "w", encoding="cp1251", errors="replace") as f:
        f.write(combined_content)

    messagebox.showinfo("Готово", f"Объединено {len(all_files)} файлов в {output_file}")
