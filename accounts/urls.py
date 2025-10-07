from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('customerDashboard/', views.customerDashboard, name='customerDashboard'),
    path('userManagement/', views.user_management, name='user_management'),
    path('track_order/<int:order_id>/', views.track_order, name='track_order'),
    path('transactions/', views.transactions, name='transactions'),
    path('recipes/', views.recipes, name='recipes'),
    path('contact/', views.contact, name='contact'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('about/', views.about, name='about'),
    path('account/', views.account, name='account'),
    path('products/', views.products, name='products'),
    path('profile/', views.profile, name='profile'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('contact/', views.contact, name='contact'),

    path('myOrders/', views.myOrders, name='myOrders'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),





    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('carts/', views.cart_list, name='cart_list'),
    path('cart-items/', views.cart_items, name='cart_items'),
    path('categories/', views.category_list, name='category_list'),
    path('orders/', views.order_list, name='order_list'),
    path('payments/', views.payment_list, name='payment_list'),
    path('products/', views.product_list, name='product_list'),
    path('variations/', views.variation_list, name='variation_list'),
    path('contact-messages/', views.contact_messages, name='contact_messages'),
    # CDMIS
    path('groups/', views.group_list, name='group_list'),
    path('activities/', views.activity_list, name='activity_list'),
    path('services/', views.service_list, name='service_list'),
    path('trainings/', views.training_list, name='training_list')
]
