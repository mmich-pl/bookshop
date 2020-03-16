from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django_countries.fields import CountryField
from PIL import Image
from random import choice
from os.path import join as path_join, isfile
import os

CATEGORY_CHOICES = (
    ('C', 'Chemistry'),
    ('B', 'Biology'),
    ('E', 'English'),
    ('G', 'Geography'),
    ('M', 'Math'),
    ('O', 'Other'),
    ('P', 'Polish'),
    ('Ph', 'Physic'),
)

LABEL_CHOICES = (
    ('S', 'success'),
    ('I', 'info'),
    ('D', 'danger'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
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


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=300)
    publisher = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(default=price)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    date = models.DateField(timezone.now())
    numbers_of_entries = models.IntegerField(default=0)
    image = models.ImageField(default=random_img, upload_to='books_img')

    def __str__(self):
        return self.title or ''

    def save(self, **kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 450 or img.width > 450:
            output_size = (450, 450)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_absolute_url(self):
        return reverse("core:product", kwargs={'slug': self.slug})

    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={'slug': self.slug})

    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={'slug': self.slug})


class OrderBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.book.title}"

    def get_total_book_price(self):
        return self.quantity * self.book.price

    def get_total_discount_book_price(self):
        return self.quantity * self.book.discount_price

    def get_amount_saved(self):
        return self.get_total_book_price() - self.get_total_discount_book_price()

    def get_final_price(self):
        if self.book.discount_price:
            return self.get_total_discount_book_price()
        return self.get_total_book_price()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(OrderBook)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name='billing_address',
                                        on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address',
                                         on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return str(self.user) or ''

    def get_total(self):
        total = 0
        for order_item in self.books.all():
            total += order_item.get_final_price()
        return total


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=10)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}, street: {self.street_address}"

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) or ''