"""
Admin command to load data from the IPS spreadsheet and store in the DB, or print data from the DB.
(reference: https://docs.djangoproject.com/en/2.2/howto/custom-management-commands/)
"""

from datetime import datetime
import pytz
from os.path import getmtime
import os

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import xlrd

Cell = apps.get_model("metrics", "Cell")
ColumnHeader = apps.get_model("metrics", "ColumnHeader")
IPFNumber = apps.get_model("metrics", "IPFNumber")
WorkSheet = apps.get_model("metrics", "WorkSheet")


# Primary command is "python manage.py digest_excel --create", though I don't remember how 'digest_excel' is configured as the command.
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named optional arguments:
        parser.add_argument('--create', action='store_true', help="Create new worksheet record", )
        parser.add_argument('--print', action='store_true', help="Print cells from last-updated sheet", )

    def handle(self, *args, **options):
        if not options['create'] and not options['print']:
            self.stdout.write("No action specified - exiting.")
            return

        excel_digester = ExcelDigester()

        if options['create']:
            self.stdout.write("Create called")
            try:
                excel_digester.digest()
            except OSError as e:
                self.stdout.write(f"Exception in create: {str(e)}")

        if options['print']:
            # Actually this has nothing to do with Excel at this point. Not a great name, then.
            self.stdout.write("Print called")
            try:
                for cell in Cell.objects.all():
                    self.stdout.write(str(cell))
                    break  # Only really want to print 1 item for now.
            except Exception as e:
                self.stdout.write(f"Exception in print: {str(e)}")


class ExcelDigester:
    def __init__(self, fname=".\\metrics\\management\\commands\\IPS component list.xlsx"):
        self.wb_path = fname  # Default path depends on command run from the project (not app) directory.
        # self.logger = logs.config.create_logger(__name__)

    def digest(self):  # TODO - Early exit when input sheet's modified time exists in DB (data already been processed)
        """ Read all data from spreadsheet and save as DB records """
        try:
            timestamp = datetime.fromtimestamp(getmtime(self.wb_path))  # Time the workbook was last modified.
            timestamp = pytz.timezone(settings.TIME_ZONE).localize(timestamp)  # Convert to timezone-aware
        except OSError:
            msg = f"Could not get last-modified time of workbook {self.wb_path}"
            raise OSError(msg)

        try:
            wb = xlrd.open_workbook(self.wb_path)
        except xlrd.biffh.XLRDError:
            raise xlrd.biffh.XLRDError(f"Error opening workbook {self.wb_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find workbook to open {self.wb_path}")

        sheet = wb.sheet_by_name("Critical Instruments Identified")

        # Create WorkSheet record:
        ws = WorkSheet(modified_time=timestamp)
        ws.save()

        # Construct list of column indexes which have a non-empty header:
        valid_cols = [i for i in range(sheet.ncols) if sheet.cell_value(0, i) is not '']

        # Build dict of IPFNumber objects (indexed by row number):
        ipf_numbers = dict()
        for row in range(1, sheet.nrows):
            ipf_numbers[row] = IPFNumber(value=sheet.cell_value(row, 0),
                                         row_idx=row + 1,
                                         tag=sheet.cell_value(row, 1),
                                         worksheet=ws)
            ipf_numbers[row].save()

        # Build dict of ColumnHeader objects (indexed by column number):
        column_headers = dict()
        for col in valid_cols:
            column_headers[col] = ColumnHeader(value=sheet.cell_value(0, col),
                                               col_idx=col + 1,
                                               worksheet=ws)
            column_headers[col].save()

        # Build list of Cell objects:
        cells = list()
        for row in range(1, sheet.nrows):
            for col in valid_cols[1:]:
                cell = Cell(content=sheet.cell_value(row, col),
                            ipf_num=ipf_numbers[row],
                            col_header=column_headers[col],
                            worksheet=ws)
                cell.save()
                cells.append(cell)
