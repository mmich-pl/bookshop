# Generated by Django 2.2.10 on 2020-03-16 16:12

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20200316_1627'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='date',
            field=models.DateField(verbose_name=datetime.datetime(2020, 3, 16, 16, 12, 34, 716537, tzinfo=utc)),
        ),
    ]
