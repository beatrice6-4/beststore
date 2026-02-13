from django.contrib import admin

# Customize admin site
admin.site.site_header = "MAMAMAASAI BAKERS Administration"
admin.site.site_title = "MAMAMAASAI BAKERS Admin Portal"
admin.site.index_title = "Welcome to MAMAMAASAI BAKERS Admin"

# ========================= HIDE UNWANTED APPS FROM ADMIN =========================
# Unregister models from Finance app
try:
    from finance.models import FinanceRecord
    admin.site.unregister(FinanceRecord)
except:
    pass

# Unregister models from Orders app
try:
    from orders.models import Order, OrderItem
    admin.site.unregister(Order)
except:
    pass

# Unregister models from LMS app
try:
    from lms.models import Exam, Question, Choice, ExamAttempt, StudentAnswer
    admin.site.unregister(Exam)
    admin.site.unregister(Question)
    admin.site.unregister(Choice)
    admin.site.unregister(ExamAttempt)
    admin.site.unregister(StudentAnswer)
except:
    pass

# Unregister models from School app
try:
    from school.models import Department, Course, ReportingSession, Student, Enrollment, StudentFee, Result
    admin.site.unregister(Department)
    admin.site.unregister(Course)
    admin.site.unregister(ReportingSession)
    admin.site.unregister(Student)
    admin.site.unregister(Enrollment)
    admin.site.unregister(StudentFee)
    admin.site.unregister(Result)
except:
    pass