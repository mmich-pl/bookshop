from django.contrib import admin
from .models import Book, OrderBook, Order, BillingAddress, Payment

admin.site.register(Book)
admin.site.register(OrderBook)
admin.site.register(Order)
admin.site.register(BillingAddress)
admin.site.register(Payment)
