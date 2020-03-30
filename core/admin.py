from django.contrib import admin
from .models import OrderBook, Order, Address, Payment


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'street_address', 'apartment_address',
                    'country', 'zip', 'city', 'default']
    list_filter = ['default', 'country', 'city']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


admin.site.register(OrderBook)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
