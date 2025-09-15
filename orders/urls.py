from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('access_token/', views.get_access_token, name='get_access_token'),
    path('stkpush/', views.initiate_stk_push, name='initiate_stk_push'),
]
