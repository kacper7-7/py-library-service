import time
from django.core.management import BaseCommand
from django.db import connections
from psycopg2._psycopg import OperationalError


class Command(BaseCommand):
    def handle(self, *args, **options):
        db_active = False

        while not db_active:
            try:
                self.stdout.write("Connecting with database...")
                connections["default"].cursor()
                db_active = True
            except OperationalError:
                self.stdout.write("Failed connect with database")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Connected with database"))
