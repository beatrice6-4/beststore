from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ============ AUTHENTICATION ============
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgotPassword'),  # Add this
    
    # ============ PROFILE ============
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
 
    
    # ============ WISHLIST ============
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<str:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # ============ CATEGORIES ============
    path('categories/', views.categories, name='categories'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/manage/', views.manage_categories, name='manage_categories'),
    
    # ============ CONTACT ============
    path('contact/', views.contact, name='contact'),
    
    # ============ SEARCH ============
    path('search/', views.search, name='search'),
]