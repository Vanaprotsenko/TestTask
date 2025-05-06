# AutoRia Scraper

Приложение для периодического скрапинга платформы AutoRia (б/у авто) с сохранением данных в PostgreSQL и автоматическим созданием ежедневных дампов базы данных.

## Структура проекта

```
autoria_scraper/
├── app/                    # Django приложение
│   ├── core/               # Основные настройки Django
│   └── scraper/            # Приложение для скрапинга
│       ├── management/     # Команды Django для управления скрапером
│       │   └── commands/   
│       ├── admin.py        # Настройки админ-панели
│       ├── apps.py         # Конфигурация приложения
│       ├── models.py       # Модели данных
│       ├── scraper.py      # Основной код скрапера
│       ├── tasks.py        # Задачи Celery
│       └── views.py        # Представления (не используются в текущей версии)
├── dumps/                  # Папка для хранения дампов базы данных
├── .env                    # Файл с настройками приложения
├── .gitignore              # Файлы, которые следует игнорировать в git
├── docker-compose.yml      # Настройки для Docker Compose
├── Dockerfile              # Инструкции для сборки Docker-образа
├── README.md               # Документация проекта
└── requirements.txt        # Зависимости Python
```

## Настройки приложения

Настройки приложения хранятся в файле `.env` в корне проекта. Пример настроек:

```
# Django settings
DEBUG=True
SECRET_KEY=your_secret_key_change_this
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DB_NAME=autoria
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Celery settings
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Scraper settings
SCRAPER_START_URL=https://auto.ria.com/uk/car/used/
SCRAPER_MAX_PAGES=5
SCRAPER_RUN_TIME=12:00
DUMP_RUN_TIME=13:00
```

## Запуск приложения

### Через Docker Compose (рекомендуемый способ)

1. Установите Docker и Docker Compose, если они еще не установлены
2. Склонируйте репозиторий и перейдите в директорию проекта
3. Создайте файл `.env` на основе примера выше
4. Запустите приложение командой:

```bash
docker-compose up -d
```

### Ручной запуск

1. Установите PostgreSQL и Redis
2. Создайте базу данных для приложения
3. Установите зависимости Python:

```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе примера выше
5. Перейдите в директорию `app` и выполните миграции:

```bash
cd app
python manage.py migrate
```

6. Запустите Django-сервер:

```bash
python manage.py runserver
```

7. В отдельном терминале запустите Celery-worker:

```bash
cd app
celery -A core worker -l info
```

8. В отдельном терминале запустите Celery-beat:

```bash
cd app
celery -A core beat -l info
```

## Ручной запуск задач

### Запуск скрапера вручную

```bash
python manage.py run_scraper [--max-pages MAX_PAGES] [--url URL]
```

### Создание дампа базы данных вручную

```bash
python manage.py create_dump
```

## Модель данных

Основная модель данных - `Car` со следующими полями:

- `url` (строка) - URL объявления
- `title` (строка) - Заголовок объявления
- `price_usd` (число) - Цена в долларах США
- `odometer` (число) - Пробег автомобиля в километрах
- `username` (строка) - Имя продавца
- `phone_number` (строка) - Номер телефона продавца
- `image_url` (строка) - URL главного изображения
- `images_count` (число) - Количество изображений
- `car_number` (строка) - Номер автомобиля
- `car_vin` (строка) - VIN-код автомобиля
- `location` (строка) - Местоположение
- `datetime_found` (дата/время) - Дата и время создания записи

## Периодические задачи

Приложение настроено на автоматический запуск следующих задач:

1. Скрапинг данных с AutoRia - запускается ежедневно в указанное в настройках время (по умолчанию в 12:00)
2. Создание дампа базы данных - запускается ежедневно в указанное в настройках время (по умолчанию в 13:00)

Время запуска задач можно изменить в файле `.env`.