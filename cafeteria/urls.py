from django.urls import path
from cafeteria.views import (
    ItemDetailView, 
    Products,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,  
    lipa_na_mpesa,
    Cart
)
    
# app_name = 'core'

urlpatterns = [
    path('', Products, name='products'),
    path('order-summary/lipa_na_mpesa/', lipa_na_mpesa, name='lipa_na_mpesa'),
    path('order-summary/', OrderSummaryView.as_view(),name='order-summary' ), 
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'), 
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),  
]
