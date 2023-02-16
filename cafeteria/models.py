from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse 

 
class MpesaExpressPayment(models.Model):
    CheckoutRequestID = models.CharField(max_length=50, blank=True, null=True)
    MerchantRequestID = models.CharField(max_length=20, blank=True, null=True)
    ResultCode = models.IntegerField(blank=True, null=True)
    ResultDesc = models.CharField(max_length=120, blank=True, null=True)
    Amount = models.FloatField(blank=True, null=True)
    MpesaReceiptNumber = models.CharField(max_length=15, blank=True, null=True)
    Balance = models.CharField(max_length=12, blank=True, null=True)
    TransactionDate = models.DateTimeField(blank=True, null=True)
    PhoneNumber = models.CharField(max_length=13, blank=True, null=True)

    def __str__(self):
        return f"{self.PhoneNumber} has sent {self.Amount} >> {self.MpesaReceiptNumber}"

class MpesaTillPayment(models.Model):
    TransactionType =  models.CharField(max_length=12, blank=True, null=True)
    TransID = models.CharField(max_length=12, blank=True, null=True)
    TransTime = models.CharField(max_length=14, blank=True, null=True)
    TransAmount = models.CharField(max_length=12, blank=True, null=True)
    BusinessShortCode = models.CharField(max_length=6, blank=True, null=True)
    BillRefNumber = models.CharField(max_length=20, blank=True, null=True)
    InvoiceNumber = models.CharField(max_length=20, blank=True, null=True)
    OrgAccountBalance = models.CharField(max_length=12, blank=True, null=True)
    ThirdPartyTransID = models.CharField(max_length=20, blank=True, null=True)
    MSISDN = models.CharField(max_length=12, blank=True, null=True)
    FirstName = models.CharField(max_length=20, blank=True, null=True)
    MiddleName = models.CharField(max_length=20, blank=True, null=True)
    LastName = models.CharField(max_length=20, blank=True, null=True)

     

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True) 
    slug = models.SlugField()
    description = models.TextField()
    # image = models.ImageField()
    image= models.CharField(max_length=1000)
    quantity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url    

    def get_absolute_url(self):
        return reverse("product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()

    def get_items(self):
        ordered_items = 0
        for order_item in self.items.all():
            ordered_items += self.quantity
        # if self.coupon:
        #     total -= self.coupon.amount
        print(ordered_items)
        return ordered_items

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE) 
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False) 
    paid = models.BooleanField(default = False) 
    received = models.BooleanField(default=False) 
    discharged = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.phone

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        # if self.coupon:
        #     total -= self.coupon.amount
        return total

 

 