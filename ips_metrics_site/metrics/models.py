from django.db import models

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
