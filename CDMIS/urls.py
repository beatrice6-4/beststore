from . import views
from django.urls import path
from .views import UserListView, UserUpdateView, UserDeleteView, activate_user, GroupUpdateView, GroupDeleteView

app_name = 'cdmis'

urlpatterns = [
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/add/', views.GroupCreateView.as_view(), name='group_add'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('payments/', views.PaymentListView.as_view(), name='payment_list'),
    path('payments/add/', views.PaymentCreateView.as_view(), name='payment_add'),
    path('activities/', views.ActivityListView.as_view(), name='activity_list'),
    path('activities/add/', views.ActivityCreateView.as_view(), name='activity_add'),
    path('trainings/', views.TrainingListView.as_view(), name='training_list'),
    path('trainings/add/', views.TrainingCreateView.as_view(), name='training_add'),
    path('services/', views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('finance/', views.FinanceView.as_view(), name='finance'),
    path('groups/<int:pk>/edit/', views.GroupUpdateView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),
    path('payments/download/pdf/<date>/', views.download_payments_pdf_by_date, name='download_payments_pdf_by_date'),
    path('contact-messages/', views.contact_messages, name='contact_messages'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/edit/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('users/<int:pk>/activate/', views.activate_user, name='user_activate'),
    path('orders/', views.order_list, name='order_list'),
    path('reports/', views.cdmis_reports, name='reports'),
    path('case-management/', views.case_management, name='case_management'),


    path('orders/', views.order_list, name='order_list'),
    path('orders/edit/<int:pk>/', views.order_edit, name='order_edit'),
    path('orders/delete/<int:pk>/', views.order_delete, name='order_delete'),
    path('profile/', views.profile, name='profile'),
    path('groups/<int:pk>/members/', views.group_members, name='group_members'),
    path('members/upload/', views.upload_members, name='upload_members'),
    path('members/', views.member_list, name='member_list'),
    path('payments/download/<str:payment_date>/', views.download_payments_pdf_by_date, name='download_payments_by_date'),
]