from django.contrib import admin
from .models import Account, Item, Order, OrderItem, Payment

admin.site.register(Account)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Payment)
