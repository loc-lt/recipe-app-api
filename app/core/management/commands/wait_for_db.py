"""
Django command to wait for the database to be available
"""
import time
from django.db import connections

from psycopg2 import OperationalError as Psycopg2OpError

from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        """Entrypoint for command."""
        self.stdout.write("Waiting for database...")
        db_up = False
        while db_up is False:
            try:
                self.check(database=['default'])
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))

# class Command(BaseCommand):
#     """Django command to wait for database"""
#     def handle(self, *args, **kwargs):
#         """Entrypoint for command."""
#         self.stdout.write('Waiting for database...')
#         db_conn = None
#         while not db_conn:
#             try:
#                 db_conn = connections['default']
#                 db_conn.cursor()
#             except OperationalError:
#                 self.stdout.write('Database unavailable, waiting 1 second...')
#                 time.sleep(1)

#         self.stdout.write(self.style.SUCCESS('Database available!'))