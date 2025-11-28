from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    # Dashboard
    path('', views.school_dashboard, name='dashboard'),

    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/update/', views.DepartmentUpdateView.as_view(), name='department_update'),

    # Courses
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/create/', views.CourseCreateView.as_view(), name='course_create'),
    path('courses/<int:pk>/update/', views.CourseUpdateView.as_view(), name='course_update'),

    # Students
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),  # ✅ CHANGED
    path('students/<int:pk>/update/', views.StudentUpdateView.as_view(), name='student_update'),  # ✅ CHANGED
    path('students/create/', views.StudentCreateView.as_view(), name='student_create'),

    # Sessions
    path('sessions/', views.SessionListView.as_view(), name='session_list'),
    path('sessions/create/', views.SessionCreateView.as_view(), name='session_create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session_detail'),
    path('sessions/<int:pk>/edit/', views.SessionUpdateView.as_view(), name='session_update'),

    # Enrollments
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/create/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('enrollments/<int:pk>/edit/', views.EnrollmentFormView.as_view(), name='enrollment_update'),
    # Fees
    path('fees/', views.StudentFeeListView.as_view(), name='fee_list'),
    path('fees/<int:pk>/', views.StudentFeeDetailView.as_view(), name='fee_detail'),
    path('fees/create/', views.StudentFeeCreateView.as_view(), name='fee_create'),
    path('fees/<int:pk>/update/', views.StudentFeeUpdateView.as_view(), name='fee_update'),

    # Results
    path('results/', views.ResultListView.as_view(), name='result_list'),
    path('results/<int:pk>/', views.ResultDetailView.as_view(), name='result_detail'),
    path('results/create/', views.ResultCreateView.as_view(), name='result_create'),
    path('results/<int:pk>/update/', views.ResultUpdateView.as_view(), name='result_update'),
]