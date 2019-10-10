from django.db import models

from xlrd.xldate import xldate_as_datetime

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
            return xldate_as_datetime(int(float(self.content)), 0)
        else:
            return self.content
