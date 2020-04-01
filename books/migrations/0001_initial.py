# Generated by Django 2.2.10 on 2020-04-01 11:15

import books.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=300)),
                ('publisher', models.CharField(max_length=100)),
                ('price', models.FloatField()),
                ('discount_price', models.FloatField(blank=True, null=True)),
                ('condition', models.CharField(choices=[('VG', 'Very Good'), ('G', 'Good'), ('M', 'Medium'), ('B', 'Bad'), ('VB', 'very bad')], max_length=2)),
                ('category', models.CharField(choices=[('Chemistry', 'Chemistry'), ('Biology', 'Biology'), ('English', 'English'), ('Geography', 'Geography'), ('Math', 'Math'), ('Other', 'Other'), ('Polish', 'Polish'), ('Physic', 'Physic')], max_length=20)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('numbers_of_entries', models.IntegerField(default=0)),
                ('amount', models.PositiveSmallIntegerField(default=0)),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.ImageField(default=books.models.random_img, upload_to=books.models.content_file_name)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='books.Book')),
            ],
        ),
    ]
