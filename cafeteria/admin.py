from django.contrib import admin

from .models import Item, OrderItem, Order


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered', 
                    'received', 
                    'discharged' 
                    ]
    # list_display_links = [
    #     'user',
    #     'address', 
    # ]
    list_filter = ['ordered', 
                   'received', 
                   'discharged']
    search_fields = [
        'user__phone', 
    ]
    # actions = [make_refund_accepted]


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'price',
        'discount_price',
        'image',
        'quantity'
    ]
    list_filter = ['name', 'price', 'quantity']
    search_fields = ['name']

# class AddressAdmin(admin.ModelAdmin):
#     list_display = [
#         'user',
#         'ID_NO',  
#         'county'
#     ]
#     list_filter = ['user', 'ID_NO', 'county']
#     search_fields = ['user', 'ID_NO']
admin.site.register(Item,ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)  

from .models import MpesaExpressPayment,MpesaTillPayment


class MpesaExpressPaymentAdmin(admin.ModelAdmin):
    list_display = ("PhoneNumber", "Amount", "MpesaReceiptNumber", "TransactionDate")

admin.site.register(MpesaExpressPayment,MpesaExpressPaymentAdmin)


class MpesaTillPaymentAdmin(admin.ModelAdmin):
    list_display = ("MSISDN", "TransAmount", "TransID", "TransTime")

admin.site.register(MpesaTillPayment,MpesaTillPaymentAdmin)

