# Primitive DB

Простая база данных с командным интерфейсом, написанная на Python. Поддерживает создание таблиц, CRUD-операции, декораторы для безопасности и производительности, а также красивый вывод данных в консоли.

База данных хранит мета-данные о всех таблицах в виде JSON-файла `db_meta`:

```JSON
{
    "users": {
        "ID": "int",
        "name": "str",
        "age": "int",
        "is_active": "bool"
    }
}
```

И сами данные таблицы внутри директории `.primitive_db/data/<имя_таблицы>.json`:

```JSON
[
    {
        "ID": 1,
        "name": "David",
        "age": 35,
        "is_active": true
    }
]
```

## Установка

### Из исходного кода

Клонируйте репозиторий:

```commandline
git clone <git@github.com:fenrirg6/project_2_Elskas_M25_555.git>
cd maga_py_project_2_simple_db
```

Установите пакет через Poetry:

```commandline
poetry install
```

Или с Makefile:

```commandline
make install
```

Build с Makefile:

```commandline
make build
```

Установка пакетов:

```commandline
make package-install
```

## Использование

Запустите базу данных командой:

```commandline
database
```

## Управление таблицами

### Доступные команды

- `create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> ...` - создать таблицу
- `list_tables` - показать список всех таблиц
- `drop_table <имя_таблицы>` - удалить таблицу
- `help` - показать справку
- `exit` - выйти из программы

### Поддерживаемые типы данных

- `int` - целые числа
- `str` - строки
- `bool` - логические значения

**Примечание:** Столбец `ID:int` добавляется автоматически в каждую таблицу в качестве уникального идентификатора если **не был задан в явном виде**.

### Пример использования

**Демонстрация процесса в asciinema:**

[![asciicast](https://asciinema.org/a/bg64SsN3wlNkxTaBnSahx84bw.svg)](https://asciinema.org/a/bg64SsN3wlNkxTaBnSahx84bw)

```commandline
$ database
```

1. Для **создания таблицы** введите команду:

```commandline
create_table users name:str age:int is_active:bool
```

Вывод покажет:

```commandline
Успешно: таблица 'users' успешно создана со столбцами name, age, is_active.
Данные сохранены.
```

2. Для **проверки создания** введите команду:

```commandline
list_tables
```

Вывод:

```commandline
- users
```

3. Для **удаления таблицы** введите команду:

```commandline
drop_table users
```

**Важно:**

Команда удаляет данные как из db_meta.json, так и из директории data.

Вывод:

```commandline
Успешно: таблица 'users' удалена.
```

4. **Выход из программы**:

```commandline
exit
```

Вывод:

```commandline
Выход из программы.
```

После чего программа завершит свою работу.

## CRUD-операции

### Доступные команды

- `<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...)` - создать запись.
- `<command> select from <имя_таблицы> where <столбец> = <значение>` - прочитать записи по условию.
- `<command> select from <имя_таблицы>` - прочитать все записи.
- `<command> update <имя_таблицы> set <столбец1> = <новое_значение1> where <столбец_условия> = <значение_условия>` - обновить запись.
- `<command> delete from <имя_таблицы> where <столбец> = <значение>` - удалить запись.
- `<command> info <имя_таблицы>` - вывести информацию о таблице.

### Пример использования

**Демонстрация в asciinema:**

[![asciicast](https://asciinema.org/a/a5BY8T6IsWcbOVW1Mnb79HPWV.svg)](https://asciinema.org/a/a5BY8T6IsWcbOVW1Mnb79HPWV)

```commandline
$ database
```
1. Для **добавления записи** в таблицу введите:

```commandline
insert into users values ("Sergei", 28, True)
```

**Важно:**
- Значения строкового типа должны быть в кавычках: `"Segei"` или `'Sergei'`
- Булевы значения: `true`/`True` или `false`/`False` (без кавычек)
- Значение ID генерируется автоматически и не указывается

Вывод:

```commandline
Успешно: запись в ID = 1 добавлена в таблицу users.
```

2. Проверка добавления записи в таблицу, подходит также для **чтения**:

```commandline
select from users
```

Можно **читать по условию** (через `where`):

```commandline
select from users where name="Sergey"
```

Вывод:

```commandline
+----+--------+-----+-----------+
| ID |  name  | age | is_active |
+----+--------+-----+-----------+
| 1  | Sergei |  28 |    True   |
+----+--------+-----+-----------+
```

3. **Обновление записи** по условию:

```commandline
update users set name="Sergeyyyyy" where ID=1
```

Вывод:

```commandline
Успешно: запись с ID=1 успешно обновлена.
```

4. **Удаление записи** по условию:

```commandline
delete from users where name="Sergeyyyyy"
```

Вывод:

```commandline
Успешно: запись c ID=1 успешно удалена из таблицы
```

5. Получение **справочной информации** о таблице:

```commandline
info users
```

Вывод:

```commandline
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей:0
```

## Декораторы и безопасность

### Обработка ошибок

**Демонстрация в asciinema:**



Все функции защищены декоратором `@handle_db_errors` (где это уместно), который автоматически перехватывает и обрабатывает исключения:

- `FileNotFoundError` - файл данных не найден,
- `KeyError` - таблица или столбец не существует,
- `ValueError` - ошибка валидации типов,
- `TypeError` - несоответствие типов данных.

**Пример:**

```commandline
insert into users values ("Anna", "twenty", true)
```

Вывод:

```commandline
Ошибка: значение twenty не соответствует типу int для столбца age
```

### Подтверждение опасных операций

Декоратор `@confirm_action` запрашивает подтверждение для критических операций:

- Удаление таблиц (`drop_table`)
- Удаление записей (`delete`)

**Отмена операции:**

```commandline
drop_table users
```

Вывод:

```commandline
Вы уверены, что хотите выполнить удаление таблицы? [y/n]: _
```

При выборе **не** `y` вывод:

```commandline
Операция отменена.
Операция отменена пользователем.
```

### Замер производительности

Декоратор `@log_time` измеряет время выполнения операций:

```commandline
insert into users values ("David", 35, true)
```

Вывод:

```commandline
Команда 'insert' выполнилась за 0.001 секунд.
```

### Кэширование запросов

SELECT-запросы кэшируются для ускорения повторного доступа:

```commandline
select from users
```

Вывод при первом запросе:

```commandline
Вычисление и кэширование: users_None
```

При повторном запросе:

```commandline
Результат получен из кэша: users_None
```

