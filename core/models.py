from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse

CATEGORY_CHOICES =(
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
    original_price = models.FloatField(blank=True, null=True)
    price = models.FloatField(default=0)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=2)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    numbers_of_entries = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.book.title}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    books = models.ManyToManyField(OrderBook)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username