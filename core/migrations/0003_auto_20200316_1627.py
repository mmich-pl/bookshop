# Generated by Django 2.2.10 on 2020-03-16 15:27

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200316_1358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='date',
            field=models.DateField(verbose_name=datetime.datetime(2020, 3, 16, 15, 26, 52, 848133, tzinfo=utc)),
        ),
    ]
