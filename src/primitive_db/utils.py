import json
from pathlib import Path


def load_metadata(filepath):
    """
    Загружает метаданные из JSON-файла.
    """
    try:
        file = open(filepath, "r", encoding="utf-8")
        return json.load(file)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Ошибка: '{e}'")  # just in case
        return

def save_metadata(filepath, metadata):
    """
    Сохраняет метаданные.
    """
    # создаем директорию если ее нет
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)

    try:
        file = open(filepath, "w", encoding="utf-8")
        json.dump(metadata, file, indent=4, ensure_ascii=False)
        file.close()
    except Exception as e:
        print(f"Ошибка при сохранении: '{e}'") # just in case
        return

def load_table_data(table_name, json_dir):
    """
    Загружает данные конкретной таблицы из JSON'а.
    Возвращает [], если файл не найден.
    """
    filepath = Path(json_dir)/f"{table_name}.json"

    try:
        file = open(filepath, "r", encoding="utf-8")
        return json.load(file)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Ошибка: '{e}'")  # just in case
        return

def save_table_data(table_name, data, json_dir):
    """
    Сохраняет данные конкретной таблицы в JSON.
    """
    # создаем директорию если ее нет
    Path(json_dir).mkdir(parents=True, exist_ok=True)
    filepath = Path(json_dir)/f"{table_name}.json"

    try:
        file = open(filepath, "w", encoding="utf-8")
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.close()
    except Exception as e:
        print(f"Ошибка при сохранении: '{e}'")
