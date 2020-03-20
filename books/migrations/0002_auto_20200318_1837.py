# Generated by Django 2.2.10 on 2020-03-18 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='amount',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='book',
            name='category',
            field=models.CharField(choices=[('Chemistry', 'Chemistry'), ('Biology', 'Biology'), ('English', 'English'), ('Geography', 'Geography'), ('Math', 'Math'), ('Other', 'Other'), ('Polish', 'Polish'), ('Physic', 'Physic')], max_length=20),
        ),
    ]