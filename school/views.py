from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Department, Course, Student, ReportingSession, Enrollment, StudentFee, Result
from .forms import (
    DepartmentForm, CourseForm, StudentForm, SessionForm,
    EnrollmentForm, StudentFeeForm, ResultForm
)


# ===================== ADMIN CHECK MIXIN =====================
class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('school:dashboard')


# ===================== DASHBOARD =====================
def school_dashboard(request):
    """School dashboard with overview statistics"""
    context = {
        'total_students': Student.objects.filter(status='active').count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'active_sessions': ReportingSession.objects.filter(is_active=True).count(),
        'total_fees': StudentFee.objects.aggregate(Sum('amount'))['amount__sum'] or 0,
        'collected_fees': StudentFee.objects.filter(payment_status='paid').aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0,
        'pending_fees': StudentFee.objects.filter(payment_status__in=['unpaid', 'partial']).aggregate(Sum('amount'))['amount__sum'] or 0,
        'recent_students': Student.objects.order_by('-created_at')[:5],
        'recent_results': Result.objects.order_by('-recorded_date')[:5],
    }
    return render(request, 'school/dashboard.html', context)


# ===================== DEPARTMENT VIEWS =====================
class DepartmentListView(AdminRequiredMixin, ListView):
    model = Department
    template_name = 'school/department/department_list.html'
    context_object_name = 'departments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Department.objects.all()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'school/department/department_detail.html'
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.object.courses.filter(is_active=True)
        context['students'] = self.object.students.filter(status='active')
        return context


class DepartmentCreateView(AdminRequiredMixin, CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'school/department/department_form.html'
    success_url = reverse_lazy('school:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully!')
        return super().form_valid(form)


class DepartmentUpdateView(AdminRequiredMixin, UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'school/department/department_form.html'
    success_url = reverse_lazy('school:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully!')
        return super().form_valid(form)


# ===================== COURSE VIEWS =====================
class CourseListView(ListView):
    model = Course
    template_name = 'school/course/course_list.html'
    context_object_name = 'courses'
    paginate_by = 20

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(code__icontains=search)
            )
        if department:
            queryset = queryset.filter(department_id=department)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'school/course/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enrolled_count'] = self.object.enrolled_students.count()
        context['recent_results'] = self.object.results.order_by('-recorded_date')[:10]
        return context


class CourseCreateView(AdminRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'school/course/course_form.html'
    success_url = reverse_lazy('school:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)


class CourseUpdateView(AdminRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'school/course/course_form.html'
    success_url = reverse_lazy('school:course_list')

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)


# ===================== STUDENT VIEWS =====================
class StudentListView(ListView):
    model = Student
    template_name = 'school/student/student_list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = Student.objects.all()
        search = self.request.GET.get('search')
        department = self.request.GET.get('department')
        status = self.request.GET.get('status')

        if search:
            queryset = queryset.filter(
                Q(registration_number__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if department:
            queryset = queryset.filter(department_id=department)
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class StudentDetailView(DetailView):
    model = Student
    template_name = 'school/student/student_detail.html'
    context_object_name = 'student'
    slug_field = 'registration_number'
    slug_url_kwarg = 'registration_number'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
        context['enrollments'] = student.enrollments.select_related('course', 'session')
        context['fees'] = student.fees.select_related('session')
        context['results'] = student.results.select_related('course', 'session').order_by('-recorded_date')
        context['gpa'] = self.calculate_gpa(student)
        context['total_fees'] = student.fees.aggregate(Sum('amount'))['amount__sum'] or 0
        context['paid_fees'] = student.fees.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        return context

    def calculate_gpa(self, student):
        results = student.results.all()
        if not results:
            return 0.0
        total_points = sum(r.grade_point for r in results)
        return round(total_points / len(results), 2)


class StudentCreateView(AdminRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student/student_form.html'
    success_url = reverse_lazy('school:student_list')

    def form_valid(self, form):
        messages.success(self.request, 'Student created successfully!')
        return super().form_valid(form)


class StudentUpdateView(AdminRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/student/student_form.html'
    slug_field = 'registration_number'
    slug_url_kwarg = 'registration_number'

    def get_success_url(self):
        return reverse_lazy('school:student_detail', kwargs={'registration_number': self.object.registration_number})

    def form_valid(self, form):
        messages.success(self.request, 'Student updated successfully!')
        return super().form_valid(form)


# ===================== SESSION VIEWS =====================
class SessionListView(ListView):
    model = ReportingSession
    template_name = 'school/session/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    queryset = ReportingSession.objects.order_by('-start_date')


class SessionDetailView(DetailView):
    model = ReportingSession
    template_name = 'school/session/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        context['enrollments'] = session.enrollments.count()
        context['results'] = session.results.count()
        context['fees'] = session.fees.aggregate(
            total=Sum('amount'),
            paid=Sum('paid_amount')
        )
        return context


class SessionCreateView(AdminRequiredMixin, CreateView):
    model = ReportingSession
    form_class = SessionForm
    template_name = 'school/session/session_form.html'
    success_url = reverse_lazy('school:session_list')

    def form_valid(self, form):
        messages.success(self.request, 'Session created successfully!')
        return super().form_valid(form)


# ===================== ENROLLMENT VIEWS =====================
class EnrollmentListView(ListView):
    model = Enrollment
    template_name = 'school/enrollment/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Enrollment.objects.select_related('student', 'course', 'session')
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_enrolled'] = Enrollment.objects.filter(status='enrolled').count()
        return context


class EnrollmentCreateView(AdminRequiredMixin, CreateView):
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'school/enrollment/enrollment_form.html'
    success_url = reverse_lazy('school:enrollment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Student enrolled successfully!')
        return super().form_valid(form)


# ===================== FEE VIEWS =====================
class StudentFeeListView(ListView):
    model = StudentFee
    template_name = 'school/fee/fee_list.html'
    context_object_name = 'fees'
    paginate_by = 20

    def get_queryset(self):
        queryset = StudentFee.objects.select_related('student', 'session')
        search = self.request.GET.get('search')
        status = self.request.GET.get('status')
        fee_type = self.request.GET.get('fee_type')

        if search:
            queryset = queryset.filter(
                Q(student__registration_number__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search)
            )
        if status:
            queryset = queryset.filter(payment_status=status)
        if fee_type:
            queryset = queryset.filter(fee_type=fee_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_amount'] = StudentFee.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        context['paid_amount'] = StudentFee.objects.aggregate(Sum('paid_amount'))['paid_amount__sum'] or 0
        context['pending_amount'] = context['total_amount'] - context['paid_amount']
        return context


class StudentFeeDetailView(DetailView):
    model = StudentFee
    template_name = 'school/fee/fee_detail.html'
    context_object_name = 'fee'


class StudentFeeCreateView(AdminRequiredMixin, CreateView):
    model = StudentFee
    form_class = StudentFeeForm
    template_name = 'school/fee/fee_form.html'
    success_url = reverse_lazy('school:fee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fee record created successfully!')
        return super().form_valid(form)


class StudentFeeUpdateView(AdminRequiredMixin, UpdateView):
    model = StudentFee
    form_class = StudentFeeForm
    template_name = 'school/fee/fee_form.html'
    success_url = reverse_lazy('school:fee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fee record updated successfully!')
        return super().form_valid(form)


# ===================== RESULT VIEWS =====================
class ResultListView(ListView):
    model = Result
    template_name = 'school/result/result_list.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        queryset = Result.objects.select_related('student', 'course', 'session')
        search = self.request.GET.get('search')
        grade = self.request.GET.get('grade')

        if search:
            queryset = queryset.filter(
                Q(student__registration_number__icontains=search) |
                Q(course__code__icontains=search)
            )
        if grade:
            queryset = queryset.filter(grade=grade)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['passed_count'] = Result.objects.filter(is_pass=True).count()
        context['failed_count'] = Result.objects.filter(is_pass=False).count()
        return context


class ResultDetailView(DetailView):
    model = Result
    template_name = 'school/result/result_detail.html'
    context_object_name = 'result'


class ResultCreateView(AdminRequiredMixin, CreateView):
    model = Result
    form_class = ResultForm
    template_name = 'school/result/result_form.html'
    success_url = reverse_lazy('school:result_list')

    def form_valid(self, form):
        messages.success(self.request, 'Result recorded successfully!')
        return super().form_valid(form)


class ResultUpdateView(AdminRequiredMixin, UpdateView):
    model = Result
    form_class = ResultForm
    template_name = 'school/result/result_form.html'
    success_url = reverse_lazy('school:result_list')

    def form_valid(self, form):
        messages.success(self.request, 'Result updated successfully!')
        return super().form_valid(form)