# AutoRia Scraper

Application for periodic scraping of the AutoRia platform (used cars) with data storage in PostgreSQL and automatic creation of daily database dumps.

## Project Structure

```
autoria_scraper/
├── app/                    # Django application
│   ├── core/               # Core Django settings
│   └── scraper/            # Scraping application
│       ├── management/     # Django commands for scraper management
│       │   └── commands/   
│       ├── admin.py        # Admin panel settings
│       ├── apps.py         # Application configuration
│       ├── models.py       # Data models
│       ├── scraper.py      # Main scraper code
│       ├── tasks.py        # Celery tasks
│       └── views.py        # Views (not used in current version)
├── dumps/                  # Folder for storing database dumps
├── .env                    # Application settings file
├── .gitignore              # Files to be ignored in git
├── docker-compose.yml      # Docker Compose settings
├── Dockerfile              # Instructions for building Docker image
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## Application Settings

Application settings are stored in the `.env` file in the project root. Example settings:

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

## Application Launch

### Via Docker Compose (recommended)

1. Install Docker and Docker Compose if not already installed
2. Clone the repository and navigate to the project directory
3. Create an `.env` file based on the example above
4. Launch the application with the command:

```bash
docker-compose up -d
```

### Manual Launch

1. Install PostgreSQL and Redis
2. Create a database for the application
3. Install Python dependencies:

```bash
pip install -r requirements.txt
```

4. Create an `.env` file based on the example above
5. Navigate to the `app` directory and run migrations:

```bash
cd app
python manage.py migrate
```

6. Launch the Django server:

```bash
python manage.py runserver
```

7. In a separate terminal, launch the Celery worker:

```bash
cd app
celery -A core worker -l info
```

8. In a separate terminal, launch Celery beat:

```bash
cd app
celery -A core beat -l info
```

## Manual Task Execution

### Run the scraper manually

```bash
python manage.py run_scraper [--max-pages MAX_PAGES] [--url URL]
```

### Create a database dump manually

```bash
python manage.py create_dump
```

## Data Model

The main data model is `Car` with the following fields:

- `url` (string) - Listing URL
- `title` (string) - Listing title
- `price_usd` (number) - Price in US dollars
- `odometer` (number) - Vehicle mileage in kilometers
- `username` (string) - Seller's name
- `phone_number` (string) - Seller's phone number
- `image_url` (string) - URL of the main image
- `images_count` (number) - Number of images
- `car_number` (string) - Vehicle registration number
- `car_vin` (string) - Vehicle VIN code
- `location` (string) - Location
- `datetime_found` (date/time) - Record creation date and time

## Periodic Tasks

The application is configured to automatically run the following tasks:

1. Scraping data from AutoRia - runs daily at the time specified in the settings (default 12:00)
2. Creating a database dump - runs daily at the time specified in the settings (default 13:00)

The task execution time can be changed in the `.env` file.