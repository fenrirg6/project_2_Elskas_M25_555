ALLOWED_DATA_TYPES = {'int', 'str', 'bool'}

def create_table(metadata, table_name, columns):
    """
    Создает новую таблицу с заданными столбцами.
    """
    # checking if table exists
    if table_name in metadata:
        return metadata, f"Ошибка: таблица {table_name} уже существует."

    parsed_columns = {}

    for column in columns:
        if ":" not in column:
            return (metadata, f"Ошибка: некорректное значение {column}. " +
                    "Принимается формат типа 'имя:тип'.")

        column_name, column_type = column.split(":", 1)
        column_name = column_name.strip()
        column_type = column_type.strip()

        # checking for input data types
        if column_type not in ALLOWED_DATA_TYPES:
            return (metadata, f"Ошибка: {column_type}." +
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

def drop_table(metadata, table_name):
    """
    Удаляет таблицу.
    """
    # check if table exists
    if table_name not in metadata:
        return (metadata, f"Ошибка: таблицы {table_name} не существует." +
                " Проверьте корректность написания.")

    # deleting the table
    del metadata[table_name]

    return metadata, f"Успешно: таблица '{table_name}' удалена."

def list_tables(metadata):
    """
    Возвращает список всех таблиц.
    """

    if not metadata:
        return "Пока не было создано ни одной таблицы."
    return "\n".join([f"- {table}" for table in metadata.keys()])