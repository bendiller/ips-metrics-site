from django.db import models

"""
The goal here is to replicate the DB model that I created in the ips-metrics-public project, which uses SQLAlchemy.
If I do that successfully, I should be able to just bring over the SQLite file from that project, change the DB 
settings, and move forward using it. I think.  
"""

# Useful resource:
# https://docs.djangoproject.com/en/2.2/topics/db/examples/many_to_one/


class WorkSheet(models.Model):
    class Meta:
        db_table = "worksheets"
        managed = False  # Because it exists before/outside the Django project; Django will not create or remove

    # id = models.IntegerField(primary_key=True)  # Probably unnecessary, leaving out for now.
    modified_time = models.DateTimeField(primary_key=True)
    # Old SQLAlchemy code:
    # __tablename__ = "worksheets"
    # id = Column(Integer, primary_key=True)
    # cells = relationship("Cell")
    # ipf_numbers = relationship("IPFNumber")  # I think these could be put into Cell; not sure yet of pros and cons
    # col_headers = relationship("ColumnHeader")  # I think these could be put into Cell; not sure yet of pros and cons
    # modified_time = Column(DateTime, unique=True)  # "last modified" time for the spreadsheet containing this data


class IPFNumber(models.Model):
    class Meta:
        unique_together = (('value', 'worksheet'), )
        db_table = "ipf_numbers"  # Django would normally assign this automatically, but this DB has tables already.
        managed = False  # Because it exists before/outside the Django project; Django will not create or remove

    """ Associates a row index with an IPS item number (which represents an instrument or interlock). """
    value = models.IntegerField()
    row_idx = models.IntegerField()
    tag = models.CharField(max_length=255)
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)
    #
    # def __str__(self):
    #     return f"{int(self.value)}: {self.tag} (row #{self.row_idx})"

    # Old SQLAlchemy code:
    # __tablename__ = "ipf_numbers"
    # value = Column(Integer, primary_key=True)  # A given IPF's row index can change; this should be the pri_key.
    # row_idx = Column(Integer)  # Row number in Excel containing this IPF number (starts with 1, not 0 as in xlrd)
    # tag = Column(String, nullable=False)  # Instrument tag or interlock number, etc.; not guaranteed to be unique!
    # worksheet_id = Column(Integer, ForeignKey('worksheets.id'), primary_key=True, )


class ColumnHeader(models.Model):
    class Meta:
        unique_together = (("value", "worksheet"), )
        db_table = "column_headers"
        managed = False  # Because it exists before/outside the Django project; Django will not create or remove
    # """ Simple object representing a column header found in the Excel spreadsheet. """
    # __tablename__ = "column_headers"
    # value = Column(String, primary_key=True)
    value = models.CharField(max_length=255)
    # col_idx = Column(Integer, nullable=False)  # Col number in Excel for this header (starts with 1, not 0 as in xlrd)
    col_idx = models.IntegerField()
    # worksheet_id = Column(Integer, ForeignKey('worksheets.id'), primary_key=True)
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)
    #
    # def __str__(self):
    #     return f"{self.col_idx}: {self.value}"


class Cell(models.Model):
    class Meta:
        db_table = "cells"
        managed = False  # Because it exists before/outside the Django project; Django will not create or remove
    # id = Column(Integer, primary_key=True)
    id = models.IntegerField(primary_key=True)
    # content = Column(String)
    content = models.CharField(max_length=255)
    # worksheet_id = Column(Integer, ForeignKey('worksheets.id'))
    worksheet = models.ForeignKey(WorkSheet, on_delete=models.CASCADE)

    # I think I need to re-work how I am using ForeignKey objects for Django. SQLAlchemy allows the use of an individual
    # field within another table as a foreign key without much in the way of constraints. Django allows this too, with
    # the `ForeignKey.to_field` parameter, but it requires that the referenced field must have `unique=True`. That's
    # not really a problem, because I had a feeling I was doing this wrong anyway.

    # row_idx = Column(Integer, ForeignKey('ipf_numbers.row_idx'))
    ipf_num = models.ForeignKey(IPFNumber, on_delete=models.CASCADE)  # Do I have to move this below...?
    # tag = Column(String, ForeignKey('ipf_numbers.tag'))  # Only here for query convenience; could be very bad practice?
    # col_idx = Column(Integer, ForeignKey('column_headers.col_idx'))
    # col_header = Column(String, ForeignKey(
    #     'column_headers.value'))  # Only here for query convenience; could be very bad practice?  # noqa
    col_header = models.ForeignKey(ColumnHeader, on_delete=models.CASCADE)
