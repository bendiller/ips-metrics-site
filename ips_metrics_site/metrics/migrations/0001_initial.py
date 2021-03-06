# Generated by Django 2.2.6 on 2019-10-10 10:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WorkSheet',
            fields=[
                ('modified_time', models.DateTimeField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='IPFNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField()),
                ('row_idx', models.IntegerField()),
                ('tag', models.CharField(max_length=255)),
                ('worksheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.WorkSheet')),
            ],
            options={
                'unique_together': {('value', 'worksheet')},
            },
        ),
        migrations.CreateModel(
            name='ColumnHeader',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('col_idx', models.IntegerField()),
                ('worksheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.WorkSheet')),
            ],
            options={
                'unique_together': {('value', 'worksheet')},
            },
        ),
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('content', models.CharField(max_length=255)),
                ('col_header', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.ColumnHeader')),
                ('ipf_num', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.IPFNumber')),
                ('worksheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metrics.WorkSheet')),
            ],
        ),
    ]
