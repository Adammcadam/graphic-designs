from django.contrib import admin
from .models import Account, Item, Order, OrderItem, Payment, Discount

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'ordered_date']

admin.site.register(Account)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Discount)
