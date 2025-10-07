# split.py
import os
import re
from tkinter import filedialog, messagebox
from utils import read_file_safely

APPDATA_FOLDER = os.path.join(os.getenv("APPDATA"), "PNXTool")
os.makedirs(APPDATA_FOLDER, exist_ok=True)
RULES_FILE = os.path.join(APPDATA_FOLDER, "rules.json")

def load_rules():
    """Загрузить правила из rules.json или вернуть стандартные, если файла нет."""
    if os.path.exists(RULES_FILE):
        try:
            import json
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # если файл кривой — вернуть стандартные правила
            pass
    return {
        "тим": ["тимбер", "вуд", "лосп"],
        "без_тим": ["синкрон", "пост"],
        "agt": ["evosoft", "evogloss", "agt"]
    }

def extract_date_from_filename(filename):
    """Ищем первую дату в формате YYYY-MM-DD в имени файла. Возвращаем строку даты или None."""
    match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
    return match.group(0) if match else None

def _sanitize_part(s: str) -> str:
    """Преобразует часть имени в безопасную для файла строку (заменяет пробелы/спецсимволы)."""
    if not s:
        return "no_name"
    # заменяем всё кроме букв, цифр, дефиса и подчёркивания на подчёркивание
    sanitized = re.sub(r'[^A-Za-z0-9\-_А-Яа-яЁё]', '_', s)
    # обрезаем слишком длинные имена
    return sanitized[:120]

def _normalize(s: str) -> str:
    """Удаляем BOM/zero-width, приводим к lower и убираем лишние пробелы."""
    if s is None:
        return ""
    s = s.replace("\ufeff", "").replace("\u200b", "")
    return s.strip().lower()

def _first_token(s: str) -> str:
    """
    Выделяем первый токен из строки (до первого разделителя, но оставляем '-' и '_'),
    например 'timber-Galif' -> 'timber-galif', 'evosoft something' -> 'evosoft'.
    """
    s = s.strip().lower()
    if not s:
        return ""
    # разделяем по любым символам кроме буквы/цифры/дефиса/подчёркивания
    parts = re.split(r'[^0-9a-zа-яё\-_]+', s, flags=re.IGNORECASE)
    return parts[0] if parts else s

def split_file():
    """Диалог выбора файла и разделение по категориям — имена файлов: <дата или исходное>_<категория>.pnx"""
    file_path = filedialog.askopenfilename(
        title="Выберите файл для разделения",
        filetypes=[("PNX файлы", "*.pnx"), ("Все файлы", "*.*")]
    )
    if not file_path:
        return

    # Загружаем и нормализуем правила: превратить каждую keywords в список нормализованных строк
    raw_categories = load_rules()
    categories = {}
    for cat, kws in raw_categories.items():
        # поддерживаем либо строку, либо список
        if isinstance(kws, str):
            kws_list = [kws]
        else:
            kws_list = kws
        norm = []
        for k in kws_list:
            nk = _normalize(k)
            if nk:
                norm.append(nk)
        categories[cat] = norm

    lines = read_file_safely(file_path).splitlines()
    output = {key: [] for key in categories}
    output["прочее"] = []

    for line in lines:
        # Берём только первое поле (до первого ;)
        first_field_raw = (line.split(";", 1)[0] if ";" in line else line)
        first_field = _normalize(first_field_raw)
        token = _first_token(first_field)

        found = False
        for cat, keywords in categories.items():
            for kw in keywords:
                # если ключ содержит пробел (фраза) — ищем её в первом поле
                if " " in kw:
                    if kw in first_field:
                        output[cat].append(line)
                        found = True
                        break
                else:
                    # отдельное слово/токен: сравниваем с первым токеном
                    # допускаем точное совпадение или совпадение по началу (startswith)
                    if token == kw or token.startswith(kw):
                        output[cat].append(line)
                        found = True
                        break
            if found:
                break

        if not found:
            output["прочее"].append(line)

    base_name, ext = os.path.splitext(os.path.basename(file_path))
    folder = os.path.dirname(file_path)

    # ищем дату
    date_part = extract_date_from_filename(base_name)

    if date_part:
        # сохраняем всё после даты, включая пробелы/символы
        rest = base_name.split(date_part, 1)[1].lstrip("_ ")  # убираем подчеркивание или пробел после даты
        prefix = f"{date_part}_{rest}" if rest else date_part
    else:
        prefix = _sanitize_part(base_name)

    created = []  # список (out_path, count_lines)
    for cat, cat_lines in output.items():
        if not cat_lines:
            continue
        # формируем имя: "<prefix> <category>.pnx"
        out_name = f"{prefix} {cat}{ext}"
        out_path = os.path.join(folder, out_name)
        try:
            with open(out_path, "w", encoding="cp1251", errors="replace") as f:
                f.write("\n".join(cat_lines))
            created.append((out_path, len(cat_lines)))
        except Exception as e:
            messagebox.showerror("Ошибка записи", f"Не удалось записать {out_name}:\n{e}")
            return

    if not created:
        messagebox.showinfo("Результат", "Ничего не создано — нет строк, соответствующих категориям.")
        return

    # Сообщение пользователю: список созданных файлов и кол-во строк
    lines_info = "\n".join([f"{os.path.basename(p)} — {cnt} строк" for p, cnt in created])
    messagebox.showinfo("Готово", f"Создано {len(created)} файлов:\n{lines_info}")
