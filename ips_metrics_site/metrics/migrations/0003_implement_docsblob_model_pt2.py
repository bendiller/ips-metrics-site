# Generated by Django 2.2.6 on 2020-01-10 20:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0002_implement_docsblob_model'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='docsblob',
            unique_together={('ipf_num', 'content')},
        ),
    ]