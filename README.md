# Парсер документации Python и PEP

Парсер документации Python и статусов PEP.

## Автор

Sergey Sokolkin — [GitHub](https://github.com/hawkxdev/)

## Tech Stack

- [Python 3.9](https://www.python.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — парсинг HTML
- [requests-cache](https://requests-cache.readthedocs.io/) — кеширование HTTP-запросов
- [tqdm](https://tqdm.github.io/) — прогресс-бары
- [PrettyTable](https://github.com/jazzband/prettytable) — табличный вывод

## Возможности

- **whats-new** — парсинг страниц "What's New in Python"
- **latest-versions** — получение списка версий Python с их статусами
- **download** — скачивание архива документации Python
- **pep** — статистика PEP по статусам

## Установка

### 1. Клонирование репозитория

```bash
git clone git@github.com:hawkxdev/bs4_parser_pep.git
cd bs4_parser_pep
```

### 2. Создание виртуального окружения

```bash
python3.9 -m venv venv
source venv/bin/activate  # Linux/macOS
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## Использование

### Парсеры

```bash
# What's New in Python
python src/main.py whats-new

# Версии Python
python src/main.py latest-versions

# Скачивание документации
python src/main.py download

# Парсер PEP (статистика по статусам)
python src/main.py pep
```

### Опции вывода

```bash
# PrettyTable в терминал
python src/main.py pep -o pretty

# CSV-файл в директорию results/
python src/main.py pep -o file

# Очистка кеша перед запуском
python src/main.py pep -c
```

## Структура проекта

```
bs4_parser_pep/
├── src/
│   ├── main.py          # Точка входа, функции парсинга
│   ├── configs.py        # CLI-аргументы, настройка логирования
│   ├── constants.py     # URL, пути, EXPECTED_STATUS
│   ├── outputs.py       # Вывод: терминал, PrettyTable, CSV
│   ├── utils.py         # HTTP-запросы, поиск тегов
│   ├── exceptions.py    # Кастомные исключения
│   ├── results/         # CSV-файлы с результатами
│   ├── logs/            # Логи парсера
│   └── downloads/       # Скачанные архивы
└── tests/               # Тесты
```

## Тестирование

```bash
# Запуск тестов
pytest

# Проверка стиля кода
flake8 src/
```
