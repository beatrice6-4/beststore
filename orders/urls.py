from django.urls import path
from . import views


app_name = 'orders'


urlpatterns = [
    path('place-order/', views.placeOrder, name='placeOrder'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('list/', views.order_list, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('paid-orders/', views.paidOrders, name='paidOrders'),
    path('api/paid-orders/', views.paid_orders_api, name='paid_orders_api'),
    path('payments/', views.payments, name='payments'),
    
    path('access_token/', views.get_access_token, name='get_access_token'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
   
    path('payments/<str:order_number>/', views.payments, name='payments'),

    
    path('payments/<str:order_id>/', views.payments, name='payments'),
    path('paidOrders/', views.paidOrders, name='paidOrders'),
    path('api/orders', views.paid_orders_api, name='paid_orders_api'),


    path('mpesa/<str:order_id>/', views.mpesa_payment, name='mpesa_payment'),

    path('check-account-balance/', views.check_account_balance, name='check_account_balance'),
    path('mpesa/balance/result/', views.mpesa_balance_result, name='mpesa_balance_result'),
    path('check-transaction-status/', views.transaction_status_view, name='check_transaction_status'),

    path('transactions/portal/', views.transaction_portal, name='transaction_portal'),
]