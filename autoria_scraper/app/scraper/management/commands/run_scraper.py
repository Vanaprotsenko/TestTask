from django.core.management.base import BaseCommand
from scraper.scraper import AutoRiaScraper
import logging

logger = logging.getLogger('scraper')


class Command(BaseCommand):
    help = 'Run AutoRia scraper manually'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Custom start URL for scraping',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting AutoRia scraper...')

        try:
            scraper = AutoRiaScraper(
                start_url=options.get('url'),
            )
            cars_count = scraper.run()

            self.stdout.write(self.style.SUCCESS(f'Scraper completed successfully. Collected {cars_count} cars.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running scraper: {e}'))
            logger.error(f'Error in run_scraper command: {e}')