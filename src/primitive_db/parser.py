# src/primitive_db/parser.py
import re
import shlex

from .decorators import handle_db_errors


def where_clause_parser(where_clause):
    """
    Парсер условия WHERE в командах SELECT, DELETE, UPDATE.
    """
    if not where_clause:
        return None

    where_clause = where_clause.strip()

    # group1 [a-zA-Z0-9_] + any number of spaces + =
    # + any number of spaces + group2 [a-zA-Z0-9_] except for \n
    match = re.match(r"(\w+)\s*=\s*(.+)", where_clause)

    if not match:
        raise ValueError(f"Ошибка: некорректное условие {where_clause}")

    column = match.group(1)
    value = match.group(2)
    value_parsed = parse_value(value)

    return {column: value_parsed}

def set_clause_parser(set_clause):
    """
    Парсер конструкции SET в команде UPDATE.
    """
    if not set_clause:
        return {}

    set_dict = {}

    parts = set_clause.split(",")
    for part in parts:
        part = part.strip()
        # group1 [a-zA-Z0-9_] + any number of spaces + =
        # + any number of spaces + group2 [a-zA-Z0-9_] except for \n
        match = re.match(r'(\w+)\s*=\s*(.+)', part)

        if not match:
            raise ValueError(f"Ошибка: некорректное условие {set_clause}")

        column = match.group(1)
        value = match.group(2)
        value_parsed = parse_value(value)

        set_dict[column] = value_parsed

    return set_dict


def parse_value(value):
    """
    Парсер подаваемых значений для улучшения конвертации и юзибилити.
    """
    value_str = value.strip()

    # строки в кавычках
    if (value_str.startswith('"') and value_str.endswith('"')) or \
            (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # булеан
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False

    # число
    try:
        if '.' in value_str:
            return float(value_str)
        return int(value_str)
    except ValueError:
        # если не удалось распарсить возвращаем как строку
        return value_str

def parse_values(values):
    """
    Парсер значений, подаваемых в скобках для команды INSERT.
    """
    values_str = values.strip()

    if values_str.startswith('(') and values_str.endswith(')'):
        values_str = values_str[1:-1]

    # разбираем с shlex
    values = []
    parts = shlex.split(values_str)

    for part in parts:
        # убираем запятые
        part = part.rstrip(',')
        if part:
            values.append(parse_value(part))

    return values

# парсеры команд

@handle_db_errors
def parse_insert_command(user_input):
    """
    Парсит команду INSERT.
    """
    match = re.match(r'insert\s+into\s+(\w+)\s+values\s*(.+)',
                     user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды.")

    table_name = match.group(1)
    values_str = match.group(2)
    values = parse_values(values_str)

    return table_name, values

@handle_db_errors
def parse_select_command(user_input):
    """
    Парсит команду SELECT.
    """
    match = re.match(r'select\s+from\s+(\w+)(?:\s+where\s+(.+))?',
                     user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды.")

    table_name = match.group(1)
    where_str = match.group(2)
    where_clause = where_clause_parser(where_str) if where_str else None

    return table_name, where_clause

@handle_db_errors
def parse_update_command(user_input):
    """
    Парсит команду UPDATE.
    """
    match = re.match(r'update\s+(\w+)\s+set\s+(.+?)\s+where\s+(.+)',
                     user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды.")

    table_name = match.group(1)
    set_str = match.group(2)
    where_str = match.group(3)

    set_clause = set_clause_parser(set_str)
    where_clause = where_clause_parser(where_str)

    return table_name, set_clause, where_clause

@handle_db_errors
def parse_delete_command(user_input):
    """
    Парсит команду DELETE.
    """
    match = re.match(r'delete\s+from\s+(\w+)\s+where\s+(.+)',
                     user_input, re.IGNORECASE)
    if not match:
        raise ValueError("Некорректный формат команды.")

    table_name = match.group(1)
    where_str = match.group(2)
    where_clause = where_clause_parser(where_str)

    return table_name, where_clause