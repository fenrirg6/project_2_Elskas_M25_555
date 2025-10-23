# Primitive DB

Примитивная база данных с командным интерфейсом, написанная на Python.

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

Введите команду:

```commandline
create_table users name:str age:int is_active:bool
```

Вывод покажет:

```commandline
Успешно: таблица 'users' успешно создана со столбцами name, age, is_active.
Данные сохранены.
```

Для проверки создания введите команду:

```commandline
list_tables
```

Вывод:

```commandline
- users
```

Для удаления таблицы введите команду:

```commandline
drop_table users
```

Вывод:

```commandline
Успешно: таблица 'users' удалена.
```

Выход из программы:

```commandline
exit
```

Вывод:

```commandline
Выход из программы.
```

После чего программа завершит свою работу.
