# replace.py
import json
import os
from tkinter import messagebox
from utils import read_file_safely

# --- Папка для хранения ---
APPDATA_DIR = os.path.join(os.environ["APPDATA"], "PNXTool")
os.makedirs(APPDATA_DIR, exist_ok=True)

DEFAULT_REPLACE_RULES_FILE = os.path.join(APPDATA_DIR, "replace_rules.json")


# ---------- Работа с правилами ----------
def load_replace_rules(file_path: str = DEFAULT_REPLACE_RULES_FILE):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_replace_rules(rules, file_path: str = DEFAULT_REPLACE_RULES_FILE):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=4)


# ---------- Вспомогательные функции ----------
def _normalize_text(s: str) -> str:
    if s is None:
        return ""
    s = s.replace("\ufeff", "")
    s = s.replace("\u200b", "")
    s = s.replace("\xa0", " ")
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    return s


# ---------- Применение замен ----------
def apply_replacements_to_files(rules, file_paths, log_text_widget=None):
    """
    Применяет правила к выбранным файлам сразу, без резервных копий.
    Выводит количество замен в лог и итоговое сообщение.
    """
    if not file_paths:
        messagebox.showwarning("Внимание", "Файлы не выбраны!")
        return 0

    norm_rules = [{"old": (r.get("old") or "").strip(), "new": (r.get("new") or "").strip()}
                  for r in rules if (r.get("old") or "").strip()]

    total_replacements = 0
    applied_count = 0

    for path in file_paths:
        filename = os.path.basename(path)
        try:
            raw = read_file_safely(path)
            content = _normalize_text(raw)
            original_content = content
            file_replacements = 0

            for rule in norm_rules:
                count = content.count(rule["old"])
                if count > 0:
                    content = content.replace(rule["old"], rule["new"])
                    file_replacements += count
                    if log_text_widget:
                        log_text_widget.insert(
                            "end",
                            f"{filename}: '{rule['old']}' → '{rule['new']}' ({count} замен)\n"
                        )

            if content != original_content:
                with open(path, "w", encoding="cp1251", errors="replace") as f:
                    f.write(content)
                total_replacements += file_replacements
                applied_count += 1

        except Exception as e:
            if log_text_widget:
                log_text_widget.insert("end", f"Ошибка при обработке {filename}: {e}\n")
            continue

    if total_replacements == 0:
        messagebox.showinfo("Готово", "Совпадений не найдено, файлы не изменялись.")
    else:
        messagebox.showinfo("Готово", f"Замены применены к {applied_count} файлам. Всего замен: {total_replacements}")

    return applied_count
