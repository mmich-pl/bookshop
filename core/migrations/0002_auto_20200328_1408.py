# Generated by Django 2.2.10 on 2020-03-28 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address_type',
        ),
        migrations.AddField(
            model_name='address',
            name='city',
            field=models.CharField(default='Warszawa', max_length=30),
            preserve_default=False,
        ),
    ]