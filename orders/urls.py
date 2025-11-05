from django.urls import path
from . import views

urlpatterns = [
    path('placeOrder/', views.placeOrder, name='placeOrder'),
    path('payments/', views.payments, name='payments'),
    path('order_complete/', views.order_complete, name='order_complete'),
    path('access_token/', views.get_access_token, name='get_access_token'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('query/', views.query_stk_status, name='query_stk_status'),
    path('payments/<str:order_number>/', views.payments, name='payments'),
    path('stkpush/', views.initiate_stk_push, name='initiate_stk_push'),
    path('query/', views.query_stk_status, name='query_stk_status'),
    path('payments/<str:order_number>/', views.payments, name='payments'),
    path('transactions/', views.transactions, name='transactions'),


    path('mpesa/<str:order_number>/', views.mpesa_payment, name='mpesa_payment'),

    path('check-account-balance/', views.check_account_balance, name='check_account_balance'),
    path('mpesa/balance/result/', views.mpesa_balance_result, name='mpesa_balance_result'),
    path('check-transaction-status/', views.transaction_status_view, name='check_transaction_status'),
    path('mpesa/transaction/result/', views.mpesa_transaction_result, name='mpesa_transaction_result'),
]