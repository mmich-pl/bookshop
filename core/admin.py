from django.contrib import admin
from .models import Book, OrderBook, Order, Address, Payment


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address',
                    'country', 'zip', 'address_type', 'default']
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(Book)
admin.site.register(OrderBook)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
