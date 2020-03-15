from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django_countries.fields import CountryField

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

CONDITION_CHOICES = (
    ('VG', 'Very Good'),
    ('G', 'Good'),
    ('M', 'Medium'),
    ('B', 'Bad'),
    ('VB', 'very bad'),
)


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.TextField()
    publisher = models.TextField()
    price = models.FloatField()
    discount_price = models.FloatField(default=price)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    date = models.DateField(timezone.now())
    numbers_of_entries = models.IntegerField(default=0)

    def __str__(self):
        return self.title

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
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.books.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username
