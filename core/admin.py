from django.contrib import admin
from .models import Book, OrderBook, Order

admin.site.register(Book)
admin.site.register(OrderBook)
admin.site.register(Order)
