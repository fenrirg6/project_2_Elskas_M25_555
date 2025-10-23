import json
from pathlib import Path

METADATA_FILE = Path.cwd() / 'src' / 'db_meta.json'

def load_metadata(filepath):
    """
    Загружает метаданные из JSON-файла.
    Возвращает пустой словарь, если файл не найден.
    """
    try:
        file = open(filepath, "r", encoding="utf-8")
        return json.load(file)
    except FileNotFoundError:
        # print("Ошибка: файл не найден.")
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка: файл {filepath} поврежден.")
        return {}

def save_metadata(filepath, metadata):
    """
    Сохраняет метаданные.
    """
    if filepath is None:
        filepath = METADATA_FILE

    try:
        file = open(filepath, "w", encoding="utf-8")
        json.dump(metadata, file, indent=4, ensure_ascii=False)
        print("Данные сохранены.")
    except json.JSONDecodeError:
        print(f"Ошибка: {filepath} поврежден!") # just in case
        return


