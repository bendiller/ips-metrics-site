from datetime import datetime, timedelta
import json
import os

from django.conf import settings
from django.db import models

from xlrd.xldate import xldate_as_datetime, xldate_from_date_tuple

"""
The goal here is to replicate the DB model that I created in the ips-metrics-public project, which uses SQLAlchemy.
If I do that successfully, I should be able to just bring over the SQLite file from that project, change the DB 
settings, and move forward using it. I think.  
"""

# Useful resource:
# https://docs.djangoproject.com/en/2.2/topics/db/examples/many_to_one/


class WorkSheet(models.Model):

    modified_time = models.DateTimeField(primary_key=True)


class IPFNumber(models.Model):
    class Meta:
        unique_together = (('value', 'worksheet'), )

    """ Associates a row index with an IPS item number (which represents an instrument or interlock). """
    value = models.IntegerField()
    row_idx = models.IntegerField()
    tag = models.CharField(max_length=255)
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)


class ColumnHeader(models.Model):
    class Meta:
        unique_together = (("value", "worksheet"), )

    value = models.CharField(max_length=255)
    col_idx = models.IntegerField()
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)


class Cell(models.Model):

    id = models.IntegerField(primary_key=True)
    content = models.CharField(max_length=255)
    ipf_num = models.ForeignKey(IPFNumber, on_delete=models.CASCADE)
    col_header = models.ForeignKey(ColumnHeader, on_delete=models.CASCADE)
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)

    def __str__(self):

        return f"[{self.ipf_num.row_idx}, {self.col_header.col_idx}] - {self.col_header.value}: {self.date_or_content}"

    def is_date(self):
        try:
            float(self.content)
        except ValueError:
            # raise ValueError("Cell does not represent a date!")
            return False

        if "Date" in self.col_header.value and self.content != '':
            return True
            # Leaving this here in case it becomes useful, but I think it's better handled by the client.
            # if float(self.content) > 36526:
            #     # 36526 is the Excel datecode for 1/1/2000, which I chose arbitrarily.
            #     return True
            # else:
            #     # raise ValueError("Date appears to be before 1/1/2000 - unlikely to be valid!")
            #     return False

    @property
    def date_or_content(self):
        """ Return either datetime object converted from Excel date, or unchanged contents if not a date. """
        if self.is_date():
            return xldate_as_datetime(int(float(self.content)), 0).date()
        else:
            return self.content

    @classmethod
    def get_next_due(cls, stop_date=datetime.now() + timedelta(weeks=5200),
                     start_date=datetime.now()):

        # TODO - This can almost certainly be performed as a single query. I need to learn how to do that.

        stop = xldate_from_date_tuple(stop_date.timetuple()[0:3], 0)
        start = xldate_from_date_tuple(start_date.timetuple()[0:3], 0)

        latest_ws = WorkSheet.objects.latest('modified_time')

        due_date_cells = cls.objects.all() \
            .filter(worksheet=latest_ws) \
            .filter(col_header__value="Next Procedure Date") \
            .filter(content__gte=start) \
            .filter(content__lte=stop) \
            .order_by('content')

        # List of IPF numbers which have a Next Procedure Date between the start and stop.
        ipf_numbers = [c.ipf_num.value for c in due_date_cells]  # Should be possible to do this in the query.

        # New query gathering all Cells for the IPF Numbers identified as due between start & stop
        due_ipfs = cls.objects.all().filter(worksheet=latest_ws) \
            .filter(ipf_num__value__in=ipf_numbers)

        return due_ipfs


class DocsBlob(models.Model):
    """
    Documentation available for each IPF is highly variable, and never needs querying individually.
    Because of this, for each IPF, a simple block of JSON containing locations and names of all related documents is
    sufficient. If a case for more granular indexing presents itself later, this can be modified.
    """

    # I had initially used a ForeignKey here, but while the "value" field of an IPFNumber record contains the actual
    # IPF number, this is not guaranteed to be unique, because it's tied to an instance of the WorkSheet. On the other
    # hand, these DocsBlob objects are not tied to WorkSheet instances, and will probably be unique by "ipf_num".
    # For now, I think I'll run this without a ForeignKey.

    ipf_num = models.PositiveSmallIntegerField(unique=True)
    content = models.TextField()  # Not validating at this point, and may never, but this should always be JSON.

    @staticmethod
    def update(selected_ipf_num):
        """Traverse directory tree to update record for documents."""
        ipf_data = dict()
        for p in settings.DOC_PATHS:
            site = p.split('\\')[-1]
            for ips_item_dir in sorted(os.listdir(p)):  # Iterate over directories for each IPS item
                try:  # Parse directory names for "IPF number" and "tag data"
                    ipf_num, tag = ips_item_dir.split(sep=" - ", maxsplit=1)
                    if ipf_num == str(selected_ipf_num):
                        ipf_data["site"] = site
                        ipf_data["tag"] = tag
                        full_path = os.path.join(p, ips_item_dir)
                        ipf_data["documents"] = DocsBlob.process_doc_paths(full_path, top_level=True)
                        break
                except ValueError:
                    continue  # This one is not a valid IPS item

        # Make sure results appear to have been gathered before updating:
        if "documents" in ipf_data and len(ipf_data["documents"]) > 0:
            try:
                docs_blob = DocsBlob.objects.get(ipf_num=selected_ipf_num)
                docs_blob.content = json.dumps(ipf_data)
                docs_blob.save()
                return f"Successfully updated IPF: {selected_ipf_num}"
            except DocsBlob.DoesNotExist:
                return f"Could not retrieve DocsBlob for IPF: {selected_ipf_num}"
        else:
            return f"Something went wrong trying to parse directory structure for IPF: {selected_ipf_num}"

    @staticmethod
    def process_doc_paths(path_root, top_level=False):
        """Recursively processes directory structure, adding directories and files to "data" argument"""
        top_level_dirs = ['Drawings', 'Inspection History', 'Procedures']
        data = {}
        for item in os.listdir(path_root):  # Each item is essentially either a file or another directory
            if top_level and item not in top_level_dirs:  # Skip unwanted dirs from top level of recursive search
                continue
            if item[0] is "~":  # Used by Microsoft Office for temporary copies of files
                continue
            elif item == "Thumbs.db":  # Windows file that is not useful for these purposes.
                continue
            path_new = os.path.join(path_root, item)
            data[item] = {}
            data[item]['full_path'] = path_new
            if os.path.isfile(path_new):  # "Stop recursing" condition
                data[item]['is_file'] = True
                data[item]['sub_paths'] = {}
            elif os.path.isdir(path_new):  # Begin next level of recursion
                data[item]['is_file'] = False
                data[item]['sub_paths'] = DocsBlob.process_doc_paths(path_new)

        return data
