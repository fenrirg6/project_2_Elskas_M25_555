from prettytable import PrettyTable

from .decorators import confirm_action, handle_db_errors, log_time

ALLOWED_DATA_TYPES = {'int', 'str', 'bool'}

@handle_db_errors
def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу с заданными столбцами.
    """
    # checking if table exists
    if table_name in metadata:
        return metadata, f"Ошибка: таблица '{table_name}' уже существует."

    parsed_columns = {}

    for column in columns:
        if ":" not in column:
            return (metadata, f"Ошибка: некорректное значение '{column}'. " +
                    "Принимается формат типа 'имя:тип'.")

        column_name, column_type = column.split(":", 1)
        column_name = column_name.strip()
        column_type = column_type.strip()

        # checking for input data types
        if column_type not in ALLOWED_DATA_TYPES:
            return (metadata, f"Ошибка: '{column_type}'." +
                    f"Допустимые типы данных: {', '.join(ALLOWED_DATA_TYPES)}.")

        parsed_columns[column_name] = column_type

    # auto adding id
    table_structure = {"ID": "int"}
    table_structure.update(parsed_columns)

    # saving table
    metadata[table_name] = table_structure

    # success message
    return (metadata, f"Успешно: таблица '{table_name}' " +
            f"успешно создана со столбцами {', '.join(parsed_columns)}.")

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """
    Удаляет таблицу.
    """
    # check if table exists
    if table_name not in metadata:
        return (metadata, f"Ошибка: таблицы '{table_name}' не существует." +
                " Проверьте корректность написания.")

    # deleting the table
    del metadata[table_name]

    return metadata, f"Успешно: таблица '{table_name}' удалена."

@handle_db_errors
def list_tables(metadata):
    """
    Возвращает список всех таблиц.
    """

    if not metadata:
        return "Пока не было создано ни одной таблицы."
    return "\n".join([f"- {table}" for table in metadata.keys()])


def validate_value(value, expected_type):
    """
    Проверяет соответствие значения ожидаемому типу.
    """
    match expected_type:
        case "int":
            if isinstance(value, int) and not isinstance(value, bool):
                return True, value
            try:
                return True, int(value)
            except (ValueError, TypeError):
                return False, None

        case "str":
            if isinstance(value, str):
                return True, value
            return True, str(value)

        case "bool":
            if isinstance(value, bool):
                return True, value
            if isinstance(value, str):
                if value.lower() in ('true', '1', 'yes'):
                    return True, True
                if value.lower() in ('false', '0', 'no'):
                    return True, False
            return False, None

    return False, None

@handle_db_errors
@log_time
def insert(metadata, table_name, values, table_data):
    """
    Команда для вставки заданных кортежей в таблицу.
    """
    if table_name not in metadata:
        return metadata, f"Ошибка: таблицы '{table_name}' не существует."

    table_schema = metadata[table_name]
    columns = list(table_schema.keys())[1:]

    if len(values) != len(columns):
        return (table_data, f"Ошибка: ожидается '{len(columns)}' значений, " +
                           f"получено '{len(values)}' значений")

    if table_data:
        new_id = max(row["ID"] for row in table_data) + 1
    else:
        new_id = 1

    new_row = {"ID": new_id}

    for column_name, value in zip(columns, values):
        expected_type = table_schema[column_name]
        is_valid, converted_value = validate_value(value, expected_type)

        if not is_valid:
            return (table_data, f"Ошибка: значение '{value}' не соответствует " +
                    f"типу '{expected_type}' для столбца '{column_name}'")

        new_row[column_name] = converted_value

    table_data.append(new_row)
    return (table_data, f"Успешно: запись в ID = {new_id} " +
            f"добавлена в таблицу '{table_name}'.")

@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """
    Команда для чтения данных из таблиц. Возможно задавать условие.
    """
    if not where_clause:
        return table_data

    filtered_data = []

    for row in table_data:
        match = True
        for column_name, value in where_clause.items():
            if column_name not in row or row[column_name] != value:
                match = False
                break

        if match:
            filtered_data.append(row)

    return filtered_data

@handle_db_errors
def update(table_data, set_clause, where_clause=None):
    """
    Команда для обновления значений в кортежах. Возможно задавать условие.
    """
    if not where_clause:
        return table_data, "Ошибка: необходимо указать условие WHERE"

    updated_ids = []

    for row in table_data:
        match = True
        for column_name, value in where_clause.items():
            if column_name not in row or row[column_name] != value:
                match = False
                break

        if match:
            for column_name, new_value in set_clause.items():
                if column_name in row and column_name != "ID":
                    row[column_name] = new_value
            updated_ids.append(row["ID"])

    if not updated_ids:
        return table_data, "Ошибка: записи, удовлетворяющие условию, не найдены."

    ids_str = ", ".join([f"ID={id_}" for id_ in updated_ids])

    return table_data, f"Успешно: запись с '{ids_str}' успешно обновлена."

@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause=None):
    """
    Команда для удаления кортежей. Возможно задавать условие.
    """
    if not where_clause:
        return table_data, "Ошибка: укажите условие WHERE."

    deleted_ids = []
    new_table_data = []

    for row in table_data:
        match = True
        for column_name, value in where_clause.items():
            if column_name not in row or row[column_name] != value:
                match = False
                break

        if match:
            deleted_ids.append(row["ID"])
        else:
            new_table_data.append(row)

    if not deleted_ids:
        return (table_data, "Ошибка: записи, " +
                f"удовлетворяющие условию '{where_clause}', не найдены.")

    ids_str = ", ".join([f"ID={id_}" for id_ in deleted_ids])
    return new_table_data, f"Успешно: запись c '{ids_str}' успешно удалена из таблицы."

@handle_db_errors
def table_info(metadata, table_name, table_data):
    """
    Выводит справочную информацию по указанной таблице.
    """
    if table_name not in metadata:
        return f"Ошибка: таблицы '{table_name}' не существует."

    table_schema = metadata[table_name]
    columns_str = ", ".join([f"{name}:{type_}" for name, type_ in table_schema.items()])
    record_count = len(table_data)

    return (f"Таблица: {table_name}\n" +
            f"Столбцы: {columns_str}\nКоличество записей:{record_count}")

@handle_db_errors
def pretty_table_output(table_data, table_schema):
    """
    Обработчик вывода таблиц через PrettyTable.
    """
    if not table_data:
        return "Записей не найдено."

    table = PrettyTable()
    table.field_names = list(table_schema.keys())

    for row in table_data:
        table.add_row([row.get(col, '') for col in table_schema.keys()])

    return str(table)
