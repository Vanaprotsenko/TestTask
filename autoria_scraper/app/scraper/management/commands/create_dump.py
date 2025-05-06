from django.core.management.base import BaseCommand
from scraper.tasks import create_db_dump_task
import logging

logger = logging.getLogger('scraper')


class Command(BaseCommand):
    help = 'Create a database dump manually'

    def handle(self, *args, **options):
        self.stdout.write('Creating database dump...')

        try:
            result = create_db_dump_task.delay()
            dump_file = result.get(timeout=600)

            self.stdout.write(self.style.SUCCESS(f'Database dump created successfully: {dump_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating database dump: {e}'))
            logger.error(f'Error in create_dump command: {e}')
