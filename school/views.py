from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import (
    Department, Course, ReportingSession, Student, 
    Enrollment, StudentFee, Result
)


# ==================== DASHBOARD VIEWS ====================

@login_required
def school_dashboard(request):
    """School management dashboard"""
    context = {
        'total_students': Student.objects.filter(status='active').count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
        'current_session': ReportingSession.objects.filter(is_current=True).first(),
        'total_fees_collected': StudentFee.objects.filter(payment_status='paid').aggregate(
            total=Sum('paid_amount')
        )['total'] or 0,
        'total_fees_pending': StudentFee.objects.filter(payment_status__in=['unpaid', 'partial']).aggregate(
            total=Sum('paid_amount')
        )['total'] or 0,
    }
    return render(request, 'school/dashboard.html', context)


# ==================== DEPARTMENT VIEWS ====================

class DepartmentListView(LoginRequiredMixin, ListView):
    """List all departments"""
    model = Department
    template_name = 'school/departments/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10

    def get_queryset(self):
        queryset = Department.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    """View department details"""
    model = Department
    template_name = 'school/departments/department_detail.html'
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        department = self.get_object()
        context['courses'] = department.courses.filter(is_active=True)
        context['students'] = department.students.filter(status='active')
        context['total_students'] = context['students'].count()
        return context


class DepartmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create new department"""
    model = Department
    template_name = 'school/departments/department_form.html'
    fields = ['name', 'code', 'description', 'head_of_department']
    success_url = reverse_lazy('school:department_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully!')
        return super().form_valid(form)


class DepartmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update department"""
    model = Department
    template_name = 'school/departments/department_form.html'
    fields = ['name', 'code', 'description', 'head_of_department', 'is_active']
    success_url = reverse_lazy('school:department_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully!')
        return super().form_valid(form)


# ==================== COURSE VIEWS ====================

class CourseListView(LoginRequiredMixin, ListView):
    """List all courses"""
    model = Course
    template_name = 'school/courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 15

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True).select_related('department')
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        if department:
            queryset = queryset.filter(department__id=department)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_department'] = self.request.GET.get('department', '')
        return context


class CourseDetailView(LoginRequiredMixin, DetailView):
    """View course details"""
    model = Course
    template_name = 'school/courses/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        context['enrolled_students'] = course.enrolled_students.filter(status='active')
        context['total_enrolled'] = context['enrolled_students'].count()
        context['results'] = course.results.all().select_related('student', 'session')
        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create new course"""
    model = Course
    template_name = 'school/courses/course_form.html'
    fields = ['name', 'code', 'department', 'credits', 'lecturer', 'description']
    success_url = reverse_lazy('school:course_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update course"""
    model = Course
    template_name = 'school/courses/course_form.html'
    fields = ['name', 'code', 'department', 'credits', 'lecturer', 'description', 'is_active']
    success_url = reverse_lazy('school:course_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)


# ==================== STUDENT VIEWS ====================

class StudentListView(LoginRequiredMixin, ListView):
    """List all students"""
    model = Student
    template_name = 'school/students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.all().select_related('department')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        department = self.request.GET.get('department')
        
        if search:
            queryset = queryset.filter(
                Q(registration_number__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if status:
            queryset = queryset.filter(status=status)
        if department:
            queryset = queryset.filter(department__id=department)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['statuses'] = Student.STATUS_CHOICES
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_status'] = self.request.GET.get('status', '')
        context['selected_department'] = self.request.GET.get('department', '')
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    """View student details"""
    model = Student
    template_name = 'school/students/student_detail.html'
    context_object_name = 'student'
    slug_field = 'registration_number'
    slug_url_kwarg = 'registration_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        context['enrollments'] = student.enrollments.all().select_related('course', 'session')
        context['fees'] = student.fees.all().select_related('session')
        context['results'] = student.results.all().select_related('course', 'session')
        context['gpa'] = self.calculate_gpa(student)
        context['total_paid'] = student.fees.filter(payment_status='paid').aggregate(
            total=Sum('paid_amount')
        )['total'] or 0
        context['total_owed'] = sum([fee.balance for fee in student.fees.all()])
        return context

    def calculate_gpa(self, student):
        results = student.results.all()
        if not results:
            return 0.0
        total_grade_points = sum([result.grade_point for result in results])
        return total_grade_points / results.count()


class StudentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create new student"""
    model = Student
    template_name = 'school/students/student_form.html'
    fields = [
        'registration_number', 'first_name', 'last_name', 'email', 
        'phone_number', 'date_of_birth', 'gender', 'department', 
        'address', 'guardian_name', 'guardian_phone'
    ]
    success_url = reverse_lazy('school:student_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)


class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update student"""
    model = Student
    template_name = 'school/students/student_form.html'
    fields = [
        'registration_number', 'first_name', 'last_name', 'email', 
        'phone_number', 'date_of_birth', 'gender', 'department', 
        'address', 'guardian_name', 'guardian_phone', 'status'
    ]
    slug_field = 'registration_number'
    slug_url_kwarg = 'registration_number'

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('school:student_detail', kwargs={
            'registration_number': self.object.registration_number
        })


# ==================== SESSION VIEWS ====================

class SessionListView(LoginRequiredMixin, ListView):
    """List all reporting sessions"""
    model = ReportingSession
    template_name = 'school/sessions/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_session'] = ReportingSession.objects.filter(is_current=True).first()
        return context


class SessionDetailView(LoginRequiredMixin, DetailView):
    """View session details"""
    model = ReportingSession
    template_name = 'school/sessions/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        context['enrollments'] = session.enrollments.count()
        context['results'] = session.results.all()
        context['fees'] = session.fees.all()
        context['passed_count'] = session.results.filter(is_pass=True).count()
        context['failed_count'] = session.results.filter(is_pass=False).count()
        return context


class SessionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create new session"""
    model = ReportingSession
    template_name = 'school/sessions/session_form.html'
    fields = ['name', 'semester', 'start_date', 'end_date', 'is_current', 'is_active']
    success_url = reverse_lazy('school:session_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        if form.cleaned_data['is_current']:
            ReportingSession.objects.filter(is_current=True).update(is_current=False)
        messages.success(self.request, 'Session created successfully!')
        return super().form_valid(form)


# ==================== ENROLLMENT VIEWS ====================

class EnrollmentListView(LoginRequiredMixin, ListView):
    """List all enrollments"""
    model = Enrollment
    template_name = 'school/enrollments/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Enrollment.objects.all().select_related('student', 'course', 'session')
        session = self.request.GET.get('session')
        if session:
            queryset = queryset.filter(session__id=session)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = ReportingSession.objects.filter(is_active=True)
        context['selected_session'] = self.request.GET.get('session', '')
        return context


class EnrollmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Enroll student in course"""
    model = Enrollment
    template_name = 'school/enrollments/enrollment_form.html'
    fields = ['student', 'course', 'session']
    success_url = reverse_lazy('school:enrollment_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Student enrolled successfully!')
        return super().form_valid(form)


# ==================== FEES VIEWS ====================

class StudentFeeListView(LoginRequiredMixin, ListView):
    """List student fees"""
    model = StudentFee
    template_name = 'school/fees/fee_list.html'
    context_object_name = 'fees'
    paginate_by = 20

    def get_queryset(self):
        queryset = StudentFee.objects.all().select_related('student', 'session')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(payment_status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statuses'] = StudentFee.PAYMENT_STATUS_CHOICES
        context['total_collected'] = StudentFee.objects.filter(
            payment_status='paid'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        context['total_pending'] = StudentFee.objects.exclude(
            payment_status='paid'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        return context


class StudentFeeDetailView(LoginRequiredMixin, DetailView):
    """View fee details"""
    model = StudentFee
    template_name = 'school/fees/fee_detail.html'
    context_object_name = 'fee'


class StudentFeeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create fee record"""
    model = StudentFee
    template_name = 'school/fees/fee_form.html'
    fields = ['student', 'session', 'fee_type', 'amount', 'due_date', 'notes']
    success_url = reverse_lazy('school:fee_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Fee record created successfully!')
        return super().form_valid(form)


class StudentFeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update fee record"""
    model = StudentFee
    template_name = 'school/fees/fee_form.html'
    fields = ['student', 'session', 'fee_type', 'amount', 'paid_amount', 
              'payment_status', 'due_date', 'payment_date', 'notes']
    success_url = reverse_lazy('school:fee_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Fee record updated successfully!')
        return super().form_valid(form)


# ==================== RESULTS VIEWS ====================

class ResultListView(LoginRequiredMixin, ListView):
    """List all results"""
    model = Result
    template_name = 'school/results/result_list.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        queryset = Result.objects.all().select_related('student', 'course', 'session')
        session = self.request.GET.get('session')
        if session:
            queryset = queryset.filter(session__id=session)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = ReportingSession.objects.filter(is_active=True)
        context['selected_session'] = self.request.GET.get('session', '')
        return context


class ResultDetailView(LoginRequiredMixin, DetailView):
    """View result details"""
    model = Result
    template_name = 'school/results/result_detail.html'
    context_object_name = 'result'


class ResultCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create result record"""
    model = Result
    template_name = 'school/results/result_form.html'
    fields = ['student', 'course', 'session', 'continuous_assessment', 'exam_score']
    success_url = reverse_lazy('school:result_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Result recorded successfully!')
        return super().form_valid(form)


class ResultUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update result"""
    model = Result
    template_name = 'school/results/result_form.html'
    fields = ['student', 'course', 'session', 'continuous_assessment', 'exam_score']
    success_url = reverse_lazy('school:result_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Result updated successfully!')
        return super().form_valid(form)