from django.urls import path
from . import views

urlpatterns = [
    path('place_order/', views.place_order, name='place_order'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('mpesa_payment/', views.mpesa_payment, name='mpesa_payment'),
    path('kcb/<str:order_number>/', views.kcb_payment, name='kcb_payment')
]