from datetime import datetime, timedelta

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

        stop = xldate_from_date_tuple(stop_date.timetuple()[0:3], 0)
        start = xldate_from_date_tuple(start_date.timetuple()[0:3], 0)

        # print(f"Start: {start_date} - {start}")
        # print(f"Cutoff: {stop_date} - {stop}")

        due_date_cells = cls.objects.all() \
            .filter(col_header__value="Next Procedure Date") \
            .filter(content__gte=start) \
            .filter(content__lte=stop)\
            .order_by('content')

        # List of IPF numbers which have a Next Procedure Date between the start and stop.
        ipf_numbers = [c.ipf_num.value for c in due_date_cells]  # Should be possible to do this in the query.

        # New query gathering all Cells for the IPF Numbers identified as due between start & stop
        due_ipfs = cls.objects.all().filter(ipf_num__value__in=ipf_numbers)

        # return due_date_cells
        # return ipf_numbers
        return due_ipfs


    # @classmethod
    # def get_next_due(cls, interval_days=30):
    #     pass
    #
    #     cutoff_date = (datetime.now() + timedelta(days=interval_days))
    #     cutoff = xldate_from_date_tuple(cutoff_date.timetuple()[0:3], 0)
    #     today = xldate_from_date_tuple(datetime.now().timetuple()[0:3], 0)
    #     print(f"{cutoff_date} - {cutoff}")
    #     due_date_cells = cls.objects.all()\
    #         .filter(col_header__value="Next Procedure Date")\
    #         .filter(content__gte=today)\
    #         .filter(content__lte=cutoff).order_by('content')
    #
    #     return due_date_cells

    # Goals:
    # 1. Retrieve a list of cells with "Next Procedure Date" in a certain range (30 day, 90 day)
    # 2. Retrieve a list of cells by tag (providing relevant details)
