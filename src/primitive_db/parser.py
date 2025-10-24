# src/primitive_db/parser.py
import re
import shlex

def where_clause_parser(where_clause):
    """
    Парсит WHERE в dict.
    """
    if not where_clause:
        return None

    where_clause = where_clause.strip()

    # regex
    match = re.match(r"(\w+)\s*=\s*(.+)", where_clause)

    if not match:
        raise ValueError(f"Ошибка: некорректное условие {where_clause}")

    column = match.group(1)
    value = match.group(2)
    value_parsed = parse_value(value)

    return {column: value_parsed}

def set_clause_parser(set_clause):
    if not set_clause:
        return {}

    set_dict = {}

    parts = set_clause.split(",")
    for part in parts:
        part = part.strip()
        match = re.match(r'(\w+)\s*=\s*(.+)', part)

        if not match:
            raise ValueError(f"Ошибка: некорректное условие {set_clause}")

        column = match.group(1)
        value = match.group(2)
        value_parsed = parse_value(value)

        set_dict[column] = value_parsed

    return set_dict


def parse_value(value):

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