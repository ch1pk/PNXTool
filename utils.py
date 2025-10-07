def read_file_safely(path):
    """Пробует открыть файл в разных кодировках, возвращает текст"""
    for enc in ("utf-8", "cp1251", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    # если всё плохо — читаем с игнором ошибок
    with open(path, "r", errors="ignore") as f:
        return f.read()
