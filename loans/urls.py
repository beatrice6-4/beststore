from django.urls import path
from . import views

app_name = 'loans'

urlpatterns = [
    # User URLs
    path('', views.loan_application_list, name='application_list'),
    path('apply/', views.loan_application_create, name='application_create'),
    path('<int:pk>/', views.loan_application_detail, name='application_detail'),
    path('<int:pk>/edit/', views.loan_application_edit, name='application_edit'),
    path('<int:pk>/documents/', views.loan_documents_upload, name='documents_upload'),
    
    # Admin URLs
    path('admin/dashboard/', views.loan_admin_dashboard, name='admin_dashboard'),
    path('admin/applications/', views.loan_admin_list, name='admin_list'),
    path('admin/<int:pk>/verify/', views.loan_admin_verify, name='admin_verify'),
    path('admin/<int:pk>/disburse/', views.loan_admin_disburse, name='admin_disburse'),
    
    # API
    path('api/<int:pk>/geolocation/', views.loan_geolocation_api, name='geolocation_api'),
]
