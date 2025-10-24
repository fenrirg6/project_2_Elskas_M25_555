import shlex
from pathlib import Path

import prompt

from .constants import DATA_DIR, METADATA_FILE
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    pretty_table_output,
    select,
    table_info,
    update,
)
from .decorators import create_cacher
from .parser import (
    parse_delete_command,
    parse_insert_command,
    parse_select_command,
    parse_update_command,
)
from .utils import (
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)

# cacher для SELECT'ов
select_cache = create_cacher()

def print_help():
    """Выводит справочную информацию."""
    print("\n***Операции с данными***")
    print("Функции:")
    print("<command> insert into <имя_таблицы> values " +
          "(<значение1>, <значение2>, ...) - создать запись")
    print("<command> select from <имя_таблицы> where " +
          "<столбец> = <значение> - прочитать записи по условию")
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print("<command> update <имя_таблицы> set <столбец1> " +
          "= <новое_значение1> where <столбец_условия> " +
          "= <значение_условия> - обновить запись")
    print("<command> delete from <имя_таблицы> where " +
          "<столбец> = <значение> - удалить запись")
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

def run():
    """
    Главный цикл программы.
    """
    print_welcome()

    # главный цикл, удерживаем сессию
    while True:
        try:
            user_input = prompt.string(">>> Введите команду: ").strip()

            # разбор с shlex
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
                              "Используйте: create_table <имя_таблицы> <столбец:тип>.")
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
                        select_cache.clear()

                case "drop_table":
                    if len(args) < 2:
                        print(f"Ошибка: недостаточно аргументов в команде {command}." +
                              " Используйте: drop_table <имя_таблицы>.")
                        continue
                    table_name = args[1]

                    metadata = load_metadata(METADATA_FILE)

                    # dropping the table and returning the message
                    result = drop_table(metadata, table_name)

                    if result is None:
                        continue

                    metadata, message = result

                    # saving if no error
                    if message.startswith("Успешно"):
                        save_metadata(METADATA_FILE, metadata)

                    # dropping the corresponding JSON file
                    data_file = Path(DATA_DIR) / f"{table_name}.json"
                    if data_file.exists():
                        data_file.unlink()

                    select_cache.clear()

                case "list_tables":
                    metadata = load_metadata(METADATA_FILE)
                    print(list_tables(metadata))

                case "insert":
                    try:
                        table_name, values = parse_insert_command(user_input)

                        metadata = load_metadata(METADATA_FILE)
                        table_data = load_table_data(table_name, DATA_DIR)

                        table_data, message = insert(metadata, table_name,
                                                     values, table_data)
                        print(message)

                        if not message.startswith('Ошибка'):
                            save_table_data(table_name, table_data, DATA_DIR)
                            select_cache.clear()

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "select": # с кэшированием
                    try:
                        table_name, where_clause = parse_select_command(user_input)

                        metadata = load_metadata(METADATA_FILE)

                        if table_name not in metadata:
                            print(f'Ошибка: таблицы "{table_name}" не существует.')
                            continue

                        # создаем ключ для кэша
                        cache_key = f"{table_name}_{str(where_clause)}"

                        # используем кэш
                        def fetch_data():
                            table_data = load_table_data(table_name, DATA_DIR)
                            return select(table_data, where_clause)

                        filtered_data = select_cache(cache_key, fetch_data)

                        if filtered_data is not None:
                            print(pretty_table_output(filtered_data,
                                                      metadata[table_name]))

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "update":
                    try:
                        table_name, set_clause, where_clause =\
                            parse_update_command(user_input)

                        metadata = load_metadata(METADATA_FILE)

                        if table_name not in metadata:
                            print(f'Ошибка: таблицы "{table_name}" не существует.')
                            continue

                        table_data = load_table_data(table_name, DATA_DIR)
                        table_data, message = update(table_data,
                                                     set_clause, where_clause)
                        print(message)

                        if not message.startswith('Ошибка'):
                            save_table_data(table_name, table_data, DATA_DIR)
                            select_cache.clear()

                    except Exception as e:
                        print(f"Ошибка: {e}")

                case "delete":
                    try:
                        table_name, where_clause = parse_delete_command(user_input)

                        metadata = load_metadata(METADATA_FILE)

                        if table_name not in metadata:
                            print(f'Ошибка: таблицы "{table_name}" не существует.')
                            continue

                        table_data = load_table_data(table_name, DATA_DIR)
                        table_data, message = delete(table_data, where_clause)
                        print(message)

                        if not message.startswith('Ошибка'):
                            save_table_data(table_name, table_data, DATA_DIR)
                            select_cache.clear()

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
                    print(f"Неизвестная команда {command}.")

        except KeyboardInterrupt:
            print("\nВыполнение прервано пользователем")
            break