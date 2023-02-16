from http.client import HTTPResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.contrib.auth import logout 
from .models import Item, OrderItem, Order,MpesaExpressPayment
import requests
from requests.auth import HTTPBasicAuth
# from .access_token import generate_access_token
# from encode import generate_password 
from  . import keys
from datetime import datetime
from django.http import HttpResponse

import base64

from  . import keys


def generate_password(formatted_time):

    data_to_encode = (
        keys.business_shortCode + keys.lipa_na_mpesa_passkey + formatted_time
    )

    encoded_string = base64.b64encode(data_to_encode.encode())
    # print(encoded_string) b'MjAxOTAyMjQxOTUwNTc='

    decoded_password = encoded_string.decode("utf-8")

    return decoded_password


import requests
from requests.auth import HTTPBasicAuth

from  . import keys


def generate_access_token():

    consumer_key = keys.consumer_key
    consumer_secret = keys.consumer_secret
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    except:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret), verify=False)
        
    print(r.text)

    # json_response = (
    #     r.json()
    # )  # {'access_token': 'orfE9Dun2qqCpuXsORjcWGzvrAIY', 'expires_in': '3599'}

    # my_access_token = json_response["access_token"]

    return my_access_token


# generate_access_token()

def get_timestamp():
    unformatted_time = datetime.now()
    formatted_time = unformatted_time.strftime("%Y%m%d%H%M%S")

    return formatted_time

def Products(request):
    items= Item.objects.all()
    # ordered_items = OrderItem.get_items()
    context = {
        'items': items,
        # 'ordered_items' : ordered_items
    }
    print(context)
    return render(request, "products.html", context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            # print(self.request.user)
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")

class Cart(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            # print(self.request.user)
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")
     


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    print(order_item)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f"{order_item.item.name} added to cart.")
            return redirect("order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, f"{order_item.item.name} added to cart.")
            return redirect("products")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("products")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, f"{order_item.item.name} removed from your cart.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, f"{order_item.item.name} quantity was updated.")
            return redirect("order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("product", slug=slug)


@login_required
def lipa_na_mpesa(request):
     if request.method == 'POST':
          formatted_time = get_timestamp()
          decoded_password = generate_password(formatted_time)
          access_token = generate_access_token()

          api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

          headers = {"Authorization": "Bearer %s" % access_token}
          
          phonenumber = request.POST.get('PhoneNumber')
          amount =int(request.POST.get('Amount'))
          print(phonenumber,amount)
          payload = {
               "BusinessShortCode": keys.business_shortCode,
               "Password": decoded_password,
               "Timestamp": formatted_time,
               "TransactionType": "CustomerPayBillOnline",
               "Amount": amount,
               "PartyA": phonenumber,
               "PartyB": keys.business_shortCode,
               "PhoneNumber": phonenumber,
               "CallBackURL": "https://kerokapolytechnicshop.herokuapp.com/payment/lnm/",
               "AccountReference": "KEROKA POLY SHOP",
               "TransactionDesc": "Pay for Goods",
          } 
        #   response = requests.post(api_url, json=request, headers=headers)
          response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers = headers, json = payload)
          print(response.text.encode('utf8'))
          print(response.text)

        #   order = Order.objects.get(user=request.user, ordered=False)
        #   order.ordered = True
    #  context = {}
          return redirect('products') 
    #  return  render(request,'order_summary.html',context)


