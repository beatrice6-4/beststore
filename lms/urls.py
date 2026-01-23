from django.urls import path
from . import views

app_name = 'lms'

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/create-exam/', views.create_exam, name='create_exam'),
    path('admin/exam/<int:pk>/edit/', views.edit_exam, name='edit_exam'),
    path('admin/exam/<int:pk>/detail/', views.exam_detail, name='exam_detail'),
    path('admin/exam/<int:exam_pk>/question/create/', views.create_question, name='create_question'),
    path('admin/question/<int:question_pk>/choices/', views.add_choices, name='add_choices'),
    path('admin/question/<int:question_pk>/edit/', views.edit_question, name='edit_question'),
    path('admin/exam/<int:exam_pk>/results/', views.exam_results, name='exam_results'),
    path('admin/attempt/<int:attempt_pk>/details/', views.student_exam_details, name='student_exam_details'),
    
    # Student URLs
    path('exams/', views.exam_list, name='exam_list'),
    path('exam/<int:exam_pk>/instructions/', views.exam_instructions, name='exam_instructions'),
    path('attempt/<int:attempt_pk>/take/', views.take_exam, name='take_exam'),
    path('attempt/<int:attempt_pk>/result/', views.exam_result, name='exam_result'),
    path('my-exams/', views.my_exams, name='my_exams'),
    
    # API URLs
    path('api/attempt/<int:attempt_pk>/answer/<int:question_id>/', views.save_answer_ajax, name='save_answer_ajax'),
    path('api/attempt/<int:attempt_pk>/time/', views.get_exam_time_remaining, name='get_exam_time_remaining'),
]
