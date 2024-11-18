import time
from psycopg2 import OperationalError as Psycopg2pError

from django.db.utils import OperationalError
from django.db import connections
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    кастомная команда для ожидания пока встанет бд
    """

    help = "Command for waiting DataBase"

    def handle(self, *args, **options):
        self.stdout.write("waiting for DataBase ...")
        db_up = False
        while not db_up:
            self.stdout.write("try to connect to DataBase ")
            self.stdout.write("db_up = " + str(db_up))
            try:
                connections['default'].ensure_connection()
                db_up = True
            except (Psycopg2pError, OperationalError):
                self.stdout.write("wait, dataBase is starting")
                time.sleep(3)

        self.stdout.write('DAtaBase ready')
