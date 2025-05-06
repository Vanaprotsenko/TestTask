import os
import logging
import subprocess
from datetime import datetime
from celery import shared_task
from django.conf import settings
from .scraper import AutoRiaScraper

logger = logging.getLogger('scraper')


@shared_task
def run_scraper_task():
    logger.info("Starting scheduled scraper task")
    try:
        scraper = AutoRiaScraper()
        cars_count = scraper.run()
        logger.info(f"Scraper task completed successfully. Collected {cars_count} cars.")
        return cars_count
    except Exception as e:
        logger.error(f"Error in scraper task: {e}")
        raise


@shared_task
def create_db_dump_task():
    logger.info("Starting database dump task")
    try:
        dumps_dir = settings.DUMPS_DIR
        os.makedirs(dumps_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dump_filename = os.path.join(dumps_dir, f"autoria_db_dump_{timestamp}.sql")

        db_settings = settings.DATABASES['default']
        cmd = [
            'pg_dump',
            '-h', db_settings['HOST'],
            '-p', str(db_settings['PORT']),
            '-U', db_settings['USER'],
            '-d', db_settings['NAME'],
            '-f', dump_filename
        ]

        env = os.environ.copy()
        env['DB_PASSWORD'] = db_settings['DB_PASSWORD']

        logger.debug(f"Running command: {' '.join(cmd)}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )

        stdout, stderr = process.communicate()

        if stdout:
            logger.info(f"pg_dump stdout: {stdout.decode()}")
        if stderr:
            logger.info(f"pg_dump stderr: {stderr.decode()}")

        if process.returncode != 0:
            error_msg = f"Database dump failed with code {process.returncode}: {stderr.decode()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        if not os.path.exists(dump_filename):
            error_msg = f"Dump file was not created at {dump_filename}"
            logger.error(error_msg)
            raise Exception(error_msg)

        file_size = os.path.getsize(dump_filename)
        logger.info(f"Database dump created successfully: {dump_filename} (size: {file_size} bytes)")
        return dump_filename

    except Exception as e:
        logger.error(f"Error creating database dump: {e}", exc_info=True)
        raise
