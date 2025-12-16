# add_date.py
import os
import re
from tkinter import messagebox
from utils import read_file_safely


DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def extract_date_from_filename(filename: str):
    """Ищем первую дату YYYY-MM-DD в имени файла (без пути)."""
    m = DATE_RE.search(filename)
    return m.group(0) if m else None


def _normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.replace("\ufeff", "")
    s = s.replace("\u200b", "")
    s = s.replace("\xa0", " ")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s


def _append_date_to_line(line: str, date_str: str) -> str:
    """
    Добавляет дату в конец строки как новое поле.
    Сохраняем формат с разделителем ';' и финальным ';'.
    """
    base = line.rstrip("\n")
    if not base.strip():
        return base  # пустые строки не трогаем

    # Если строка уже заканчивается ';', то просто дописываем дату и ';'
    if base.endswith(";"):
        return base + date_str + ";"
    # Иначе добавляем через ';' и закрываем ';'
    return base + ";" + date_str + ";"


def append_date_to_files(file_paths, mode: str, manual_date: str = "", log_text_widget=None):
    """
    mode:
      - "from_filename": дату берём из имени каждого файла
      - "manual": используем manual_date для всех файлов
    Возвращает количество изменённых файлов.
    """
    if not file_paths:
        messagebox.showwarning("Внимание", "Файлы не выбраны!")
        return 0

    if mode == "manual":
        manual_date = (manual_date or "").strip()
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", manual_date):
            messagebox.showwarning("Ошибка", "Введите дату в формате YYYY-MM-DD (например 2025-12-19).")
            return 0

    changed_files = 0

    for path in file_paths:
        filename = os.path.basename(path)

        if mode == "from_filename":
            date_str = extract_date_from_filename(filename)
            if not date_str:
                if log_text_widget:
                    log_text_widget.insert("end", f"{filename}: дата YYYY-MM-DD не найдена в имени — пропущен\n")
                continue
        else:
            date_str = manual_date

        try:
            raw = read_file_safely(path)
            content = _normalize_text(raw)
            lines = content.split("\n")

            new_lines = []
            replaced_lines = 0

            for line in lines:
                # чтобы не добавлять дату в полностью пустую последнюю строку
                if not line.strip():
                    new_lines.append(line)
                    continue
                new_lines.append(_append_date_to_line(line, date_str))
                replaced_lines += 1

            new_content = "\n".join(new_lines)

            if new_content != content:
                with open(path, "w", encoding="cp1251", errors="replace") as f:
                    f.write(new_content)
                changed_files += 1
                if log_text_widget:
                    log_text_widget.insert("end", f"{filename}: добавлена дата {date_str} в {replaced_lines} строк\n")

        except Exception as e:
            if log_text_widget:
                log_text_widget.insert("end", f"Ошибка при обработке {filename}: {e}\n")
            continue

    if changed_files == 0:
        messagebox.showinfo("Готово", "Файлы не изменялись (возможно, дата не найдена в названиях).")
    else:
        messagebox.showinfo("Готово", f"Дата добавлена. Изменено файлов: {changed_files}")

    return changed_files
