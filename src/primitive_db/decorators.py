# src/primitive_db/decorators.py
import time
from functools import wraps


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок базы данных.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            print(f"Ошибка: Файл данных не найден. ('{e}')")
            return None
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец '{e}' не найден.")
            return None
        except ValueError as e:
            print(f"Ошибка: '{e}'")
            return None
        except TypeError as e:
            print(f"Ошибка: '{e}'")
            return None
        except Exception as e:
            print(f"Ошибка (непредвиденная): '{e}'")
            return None

    return wrapper


def confirm_action(action_name):
    """
    Декоратор для запроса подтверждения "опасных" операций.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # запрашиваем подтверждение
            response = input("Вы уверены, что хотите выполнить" +
                             f"'{action_name}'? [y/n]: ").strip().lower()

            if response == 'y':
                # выполняем функцию
                return func(*args, **kwargs)
            else:
                # print("Операция отменена.")
                if len(args) > 0:
                    return args[0], "Операция отменена пользователем."

                return None, "Операция отменена пользователем."

        return wrapper
    return decorator


def log_time(func):
    """
    Декоратор для измерения времени выполнения "долгих" функции.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs)
        end_time = time.monotonic()

        elapsed_time = end_time - start_time
        print(f"Команда '{func.__name__}' выполнилась за {elapsed_time:.3f} секунд.")

        return result
    return wrapper


def create_cacher():
    """
    Создание кэширующей функции с замыканием.
    """
    cache = {}

    def cache_result(key, value_func):
        """
        Кэширует результат выполнения функции.
        """
        if key in cache:
            print(f"Результат получен из кэша: '{key}'")
            return cache[key]

        print(f"Вычисление и кэширование: '{key}'")
        result = value_func()
        cache[key] = result
        return result

    def clear_cache():
        """Очищает весь кэш."""
        cache.clear()
        print("Кэш очищен.")

    # Возвращаем обе функции
    cache_result.clear = clear_cache
    return cache_result
