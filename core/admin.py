from django.contrib import admin
from .models import Book, OrderBook, Order, BillingAddress, Payment


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']


admin.site.register(Book)
admin.site.register(OrderBook)
admin.site.register(Order, OrderAdmin)
admin.site.register(BillingAddress)
admin.site.register(Payment)
