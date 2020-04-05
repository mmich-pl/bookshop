import os
from os.path import join as path_join, isfile
from random import choice

from PIL import Image
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

CATEGORY_CHOICES = (
    ('Chemistry', 'Chemistry'),
    ('Biology', 'Biology'),
    ('English', 'English'),
    ('Geography', 'Geography'),
    ('Math', 'Math'),
    ('Other', 'Other'),
    ('Polish', 'Polish'),
    ('Physic', 'Physic'),
)

CONDITION_CHOICES = (
    ('VG', 'Very Good'),
    ('G', 'Good'),
    ('M', 'Medium'),
    ('B', 'Bad'),
    ('VB', 'very bad'),
)


def random_img():
    dir_path = 'media/default_book_image'
    return_path = 'default_book_image'
    files = [content for content in os.listdir(dir_path) if isfile(path_join(dir_path, content))]
    return path_join(return_path, choice(files))


def content_file_name(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (instance.book.slug, ext)
    return os.path.join('books_img', instance.book.slug, filename)


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=300)
    publisher = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    slug = models.SlugField()
    description = models.TextField()
    date = models.DateField(default=timezone.now)
    numbers_of_entries = models.IntegerField(default=0)
    amount = models.PositiveSmallIntegerField(default=0)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title or ''

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={'slug': self.slug})


class Photo(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='photos')
    file = models.ImageField(default=random_img, upload_to=content_file_name)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, **kwargs):
        super().save()

        img = Image.open(self.file.path)

        if img.height > 450 or img.width > 450:
            output_size = (450, 450)
            img.thumbnail(output_size)
            img.save(self.file.path)
