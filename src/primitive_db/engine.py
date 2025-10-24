import shlex
import re
import prompt
from pathlib import Path
from .utils import METADATA_FILE, DATA_DIR, load_metadata, save_metadata, load_table_data, save_table_data
from .core import (create_table, drop_table, list_tables, insert, select,
                   update, delete, pretty_table_output, table_info)
from .parser import where_clause_parser, set_clause_parser, parse_values



def print_help():
    """Выводит справочную информацию."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия> - обновить запись")
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nУправление таблицами:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

def print_welcome():
    """Выводит приветственное сообщение."""
    print("\n***База данных***")
    print_help()

def parse_insert_command(user_input):
    """
    Парсит команду INSERT.
    """
    match = re.match(r'insert\s+into\s+(\w+)\s+values\s*(.+)', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды INSERT")

    table_name = match.group(1)
    values_str = match.group(2)
    values = parse_values(values_str)

    return table_name, values

def parse_select_command(user_input):
    """
    Парсит команду SELECT.
    """
    match = re.match(r'select\s+from\s+(\w+)(?:\s+where\s+(.+))?', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды SELECT")

    table_name = match.group(1)
    where_str = match.group(2)
    where_clause = where_clause_parser(where_str) if where_str else None

    return table_name, where_clause

def parse_update_command(user_input):
    """
    Парсит команду UPDATE.
    """
    match = re.match(r'update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды UPDATE")

    table_name = match.group(1)
    set_str = match.group(2)
    where_str = match.group(3)

    set_clause = set_clause_parser(set_str)
    where_clause = where_clause_parser(where_str)

    return table_name, set_clause, where_clause


def parse_delete_command(user_input):
    """
    Парсит команду DELETE.
    """
    match = re.match(r'delete\s+from\s+(\w+)\s+where\s+(.+)', user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды DELETE")

    table_name = match.group(1)
    where_str = match.group(2)
    where_clause = where_clause_parser(where_str)

    return table_name, where_clause

def run():
    print_welcome()
    # print(METADATA_FILE) #debug print - to drop
    # print(DATA_DIR) #debug print - to drop

    # main cycle
    while True:
        try:
            user_input = prompt.string(">>> Введите команду: ").strip()
            if not user_input:
                continue

            # shlex parsing
            try:
                args = shlex.split(user_input)
            except ValueError as e:
                print(f"Ошибка парсинга: {e}")
                continue

            # handling the commands
            command = args[0].lower()

            match command:

                case "exit":
                    print("Выход из программы.")
                    break

                case "help":
                    print_help()

                case "create_table":
                    if len(args) < 3:
                        print(f"Ошибка: недостаточно аргументов в команде {command}. " +
                              f"Используйте: create_table <имя_таблицы> <столбец:тип>.")
                        continue
                    table_name = args[1]
                    column_names = args[2:]

                    metadata = load_metadata(METADATA_FILE)

                    # creating a table and getting a return message
                    metadata, message = create_table(metadata, table_name, column_names)
                    print(message)

                    # saving if no error
                    if not message.startswith("Ошибка"):
                        save_metadata(METADATA_FILE, metadata)

                case "drop_table":
                    if len(args) < 2:
                        print(f"Ошибка: недостаточно аргументов в команде {command}." +
                              f" Используйте: drop_table <имя_таблицы>.")
                        continue
                    table_name = args[1]

                    metadata = load_metadata(METADATA_FILE)

                    # dropping the table and returning the message
                    metadata, message = drop_table(metadata, table_name)
                    print(message)

                    # saving if no error
                    if not message.startswith("Ошибка"):
                        save_metadata(METADATA_FILE, metadata)

                    # dropping the corresponding JSON file
                    data_file = Path(DATA_DIR) / f"{table_name}.json"
                    if data_file.exists():
                        data_file.unlink()

                case "list_tables":
                    metadata = load_metadata(METADATA_FILE)
                    print(list_tables(metadata))

                case "insert":
                    try:
                        table_name, values = parse_insert_command(user_input)

                        metadata = load_metadata(METADATA_FILE)
                        table_data = load_table_data(table_name, DATA_DIR)

                        table_data, message = insert(metadata, table_name, values, table_data)
                        print(message)

                        if not message.startswith('Ошибка'):
                            save_table_data(table_name, table_data, DATA_DIR)

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "select":
                    try:
                        table_name, where_clause = parse_select_command(user_input)

                        metadata = load_metadata(METADATA_FILE)

                        if table_name not in metadata:
                            print(f'Ошибка: таблица "{table_name}" не существует.')
                            continue

                        table_data = load_table_data(table_name, DATA_DIR)
                        filtered_data = select(table_data, where_clause)

                        print(pretty_table_output(filtered_data, metadata[table_name]))

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "update":
                    try:
                        table_name, set_clause, where_clause = parse_update_command(user_input)

                        metadata = load_metadata(METADATA_FILE)

                        if table_name not in metadata:
                            print(f'Ошибка: таблица "{table_name}" не существует.')
                            continue

                        table_data = load_table_data(table_name, DATA_DIR)
                        table_data, message = update(table_data, set_clause, where_clause)
                        print(message)

                        if not message.startswith('Ошибка'):
                            save_table_data(table_name, table_data, DATA_DIR)

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "delete":
                    try:
                        table_name, where_clause = parse_delete_command(user_input)

                        metadata = load_metadata(METADATA_FILE)

                        if table_name not in metadata:
                            print(f'Ошибка: таблица "{table_name}" не существует.')
                            continue

                        table_data = load_table_data(table_name, DATA_DIR)
                        table_data, message = delete(table_data, where_clause)
                        print(message)

                        if not message.startswith('Ошибка'):
                            save_table_data(table_name, table_data, DATA_DIR)

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "info":
                    try:
                        if len(args) < 2:
                            print("Ошибка: не указано имя таблицы.")
                            continue

                        table_name = args[1]
                        metadata = load_metadata(METADATA_FILE)
                        table_data = load_table_data(table_name, DATA_DIR)

                        print(table_info(metadata, table_name, table_data))
                    except Exception as e:
                        print(f"Ошибка: {e}")

                case _:
                    print(f"Неизвестная команда {command}. Попробуйте снова.")

        except KeyboardInterrupt:
            print("\nВыполнение прервано пользователем")
            break