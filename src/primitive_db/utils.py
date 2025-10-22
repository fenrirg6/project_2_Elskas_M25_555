import os
import json

METADATA_FILE = "db_meta.json"

def load_metadata(filepath):
    """
    Загружает метаданные из JSON-файла.
    Возвращает пустой словарь, если файл не найден.
    """
    try:
        file = open(filepath, "r", encoding="utf-8")
        return json.load(file)
    except FileNotFoundError:
        print("Файл не найден.")
        return {}

def save_metadata(filepath, metadata):
    """
    Сохраняет метаданные.
    """
    if filepath is None:
        filepath = METADATA_FILE

    try:
        file = open(filepath, "w", encoding="utf-8")
        json.dump(metadata, file)
        print("Данные сохранены.")
    except json.JSONDecodeError:
        print(f"Ошибка: {filepath} поврежден!") # just in case
        return


