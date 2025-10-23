import shlex

import prompt

from .core import create_table, drop_table, list_tables
from .utils import METADATA_FILE, load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
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
    print_welcome()
    # METADATA_FILE = Path.cwd() / 'src' / 'db_meta.json'
    # print(METADATA_FILE)

    # main cycle
    while True:
        try:
            user_input = prompt.string("> Введите команду: ").strip()
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

                case "list_tables":
                    metadata = load_metadata(METADATA_FILE)
                    print(list_tables(metadata))

                case _:
                    print(f"Неизвестная команда {command}. Попробуйте снова.")

        except KeyboardInterrupt:
            print("\nВыполнение прервано пользователем")
            break