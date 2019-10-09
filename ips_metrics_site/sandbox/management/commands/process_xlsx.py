"""
Admin command to load all data from the IPS spreadsheet and store in the DB.
(reference: https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/)
"""

from django.core.management.base import BaseCommand, CommandError
from sandbox.models import WorkSheet, Cell, ColumnHeader, IPFNumber


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            pass
        except:
            pass
            raise CommandError("some_error_text")

        self.stdout.write("Ran command")
