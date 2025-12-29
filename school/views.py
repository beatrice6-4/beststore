from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Sum, Count, Avg, Prefetch
from django.utils import timezone
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from .models import Department, Course, Student, ReportingSession, Enrollment, StudentFee, Result, CourseUnit
from .forms import (
    DepartmentForm, CourseForm, StudentForm, SessionForm,
    EnrollmentForm, StudentFeeForm, ResultForm, CourseUnitForm
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
    """List all academic sessions"""
    model = ReportingSession
    template_name = 'school/session/session_list.html'
    context_object_name = 'sessions'
    paginate_by = 20
    queryset = ReportingSession.objects.order_by('-start_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        context['active_sessions'] = ReportingSession.objects.filter(
            start_date__lte=today,
            end_date__gte=today,
            is_active=True
        ).count()
        context['upcoming_sessions'] = ReportingSession.objects.filter(
            start_date__gt=today,
            is_active=True
        ).count()
        context['closed_sessions'] = ReportingSession.objects.filter(
            end_date__lt=today
        ).count()
        context['total_sessions'] = ReportingSession.objects.count()
        
        return context


class SessionDetailView(DetailView):
    """View session details with enrollments and results"""
    model = ReportingSession
    template_name = 'school/session/session_detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        today = timezone.now().date()
        
        # Calculate session status
        if session.start_date > today:
            context['session_status'] = 'upcoming'
            context['days_until'] = (session.start_date - today).days
        elif session.end_date < today:
            context['session_status'] = 'closed'
            context['days_ago'] = (today - session.end_date).days
        else:
            context['session_status'] = 'active'
            context['days_elapsed'] = (today - session.start_date).days
            context['remaining_days'] = (session.end_date - today).days
        
        context['enrollments'] = session.enrollments.count()
        context['results'] = session.results.count()
        context['fees'] = session.fees.aggregate(
            total=Sum('amount'),
            paid=Sum('paid_amount')
        )
        
        return context


class SessionCreateView(AdminRequiredMixin, CreateView):
    """Create a new academic session"""
    model = ReportingSession
    form_class = SessionForm
    template_name = 'school/session/session_form.html'
    success_url = reverse_lazy('school:session_list')

    def form_valid(self, form):
        messages.success(self.request, 'Session created successfully!')
        return super().form_valid(form)


class SessionUpdateView(AdminRequiredMixin, UpdateView):
    """Update an existing academic session"""
    model = ReportingSession
    form_class = SessionForm
    template_name = 'school/session/session_form.html'
    success_url = reverse_lazy('school:session_list')

    def form_valid(self, form):
        messages.success(self.request, 'Session updated successfully!')
        return super().form_valid(form)


# ===================== ENROLLMENT VIEWS =====================
class EnrollmentListView(ListView):
    """List all course enrollments with filtering"""
    model = Enrollment
    template_name = 'school/enrollment/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20

    def get_queryset(self):
        queryset = Enrollment.objects.select_related(
            'student', 'course', 'session'
        ).order_by('-enrollment_date')
        
        # Search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(student__registration_number__icontains=search) |
                Q(course__name__icontains=search) |
                Q(course__code__icontains=search)
            )
        
        # Filter by status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by session
        session_id = self.request.GET.get('session', '')
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        
        # Filter by department
        department_id = self.request.GET.get('department', '')
        if department_id:
            queryset = queryset.filter(student__department_id=department_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        context['sessions'] = ReportingSession.objects.filter(is_active=True)
        context['total_enrollments'] = Enrollment.objects.count()
        context['total_active'] = Enrollment.objects.filter(status='active').count()
        context['total_completed'] = Enrollment.objects.filter(status='completed').count()
        context['total_dropped'] = Enrollment.objects.filter(status='dropped').count()
        return context


class EnrollmentDetailView(DetailView):
    """View enrollment details"""
    model = Enrollment
    template_name = 'school/enrollment/enrollment_detail.html'
    context_object_name = 'enrollment'

    def get_queryset(self):
        return Enrollment.objects.select_related(
            'student', 'course', 'session'
        )


class EnrollmentCreateView(AdminRequiredMixin, CreateView):
    """Admin creates enrollment for student"""
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'school/enrollment/enrollment_form.html'
    success_url = reverse_lazy('school:enrollment_list')

    def form_valid(self, form):
        messages.success(self.request, 'Student enrolled successfully!')
        return super().form_valid(form)


class EnrollmentUpdateView(AdminRequiredMixin, UpdateView):
    """Admin updates enrollment"""
    model = Enrollment
    form_class = EnrollmentForm
    template_name = 'school/enrollment/enrollment_form.html'
    
    def get_success_url(self):
        return reverse_lazy('school:enrollment_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Enrollment updated successfully!')
        return super().form_valid(form)


class StudentRegistrationView(LoginRequiredMixin, TemplateView):
    """Student registration workflow after session reporting"""
    template_name = 'school/student/student_registration.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            student = Student.objects.get(registration_number=self.request.user.username)
            context['student'] = student
            
            # Get active session
            active_session = ReportingSession.objects.filter(is_active=True).first()
            context['active_session'] = active_session
            
            if active_session:
                # Get courses available for this student's department
                available_courses = Course.objects.filter(
                    department=student.department,
                    is_active=True
                )
                context['available_courses'] = available_courses
                
                # Get already enrolled courses in this session
                enrolled = Enrollment.objects.filter(
                    student=student,
                    session=active_session
                ).values_list('course_id', flat=True)
                context['enrolled_course_ids'] = list(enrolled)
        except Student.DoesNotExist:
            pass
        
        return context


class BulkEnrollmentView(AdminRequiredMixin, TemplateView):
    """Bulk register students for courses in a session"""
    template_name = 'school/enrollment/bulk_enrollment.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = ReportingSession.objects.filter(is_active=True)
        context['departments'] = Department.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        session_id = request.POST.get('session_id')
        department_id = request.POST.get('department_id')
        course_ids = request.POST.getlist('courses')
        
        try:
            session = ReportingSession.objects.get(id=session_id)
            department = Department.objects.get(id=department_id)
            
            # Get all active students in department
            students = Student.objects.filter(
                department=department,
                status='active'
            )
            
            created_count = 0
            for student in students:
                for course_id in course_ids:
                    course = Course.objects.get(id=course_id)
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        course=course,
                        session=session,
                        defaults={'status': 'active'}
                    )
                    if created:
                        created_count += 1
            
            messages.success(
                request, 
                f'Successfully created {created_count} enrollments for {len(students)} students.'
            )
            return redirect('school:enrollment_list')
        except Exception as e:
            messages.error(request, f'Error creating enrollments: {str(e)}')
            return redirect('school:bulk_enrollment')


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
    """Admin creates student fee record"""
    model = StudentFee
    form_class = StudentFeeForm
    template_name = 'school/fee/fee_form.html'
    success_url = reverse_lazy('school:fee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fee record created successfully!')
        return super().form_valid(form)


class StudentFeeUpdateView(AdminRequiredMixin, UpdateView):
    """Admin updates student fee record"""
    model = StudentFee
    form_class = StudentFeeForm
    template_name = 'school/fee/fee_form.html'
    success_url = reverse_lazy('school:fee_list')

    def form_valid(self, form):
        messages.success(self.request, 'Fee record updated successfully!')
        return super().form_valid(form)


# ===================== RESULT VIEWS =====================
class ResultListView(ListView):
    """List all course results"""
    model = Result
    template_name = 'school/result/result_list.html'
    context_object_name = 'results'
    paginate_by = 20

    def get_queryset(self):
        queryset = Result.objects.select_related('student', 'course', 'session')
        search = self.request.GET.get('search')
        grade = self.request.GET.get('grade')
        session = self.request.GET.get('session')

        if search:
            queryset = queryset.filter(
                Q(student__registration_number__icontains=search) |
                Q(student__first_name__icontains=search) |
                Q(student__last_name__icontains=search) |
                Q(course__code__icontains=search) |
                Q(course__name__icontains=search)
            )
        if grade:
            queryset = queryset.filter(grade=grade)
        if session:
            queryset = queryset.filter(session_id=session)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['passed_count'] = Result.objects.filter(is_pass=True).count()
        context['failed_count'] = Result.objects.filter(is_pass=False).count()
        context['total_results'] = Result.objects.count()
        context['sessions'] = ReportingSession.objects.filter(is_active=True)
        return context


class ResultDetailView(DetailView):
    """View individual result details"""
    model = Result
    template_name = 'school/result/result_detail.html'
    context_object_name = 'result'

    def get_queryset(self):
        return Result.objects.select_related('student', 'course', 'session')


class ResultCreateView(AdminRequiredMixin, CreateView):
    """Admin records student result"""
    model = Result
    form_class = ResultForm
    template_name = 'school/result/result_form.html'
    success_url = reverse_lazy('school:result_list')

    def form_valid(self, form):
        messages.success(self.request, 'Result recorded successfully!')
        return super().form_valid(form)


class ResultUpdateView(AdminRequiredMixin, UpdateView):
    """Admin updates student result"""
    model = Result
    form_class = ResultForm
    template_name = 'school/result/result_form.html'
    success_url = reverse_lazy('school:result_list')

    def form_valid(self, form):
        messages.success(self.request, 'Result updated successfully!')
        return super().form_valid(form)


class BulkResultUploadView(AdminRequiredMixin, TemplateView):
    """Bulk upload results for multiple students in a course"""
    template_name = 'school/result/bulk_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = ReportingSession.objects.filter(is_active=True)
        context['courses'] = Course.objects.filter(is_active=True)
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle bulk result upload via CSV or form"""
        session_id = request.POST.get('session_id')
        course_id = request.POST.get('course_id')
        
        try:
            session = ReportingSession.objects.get(id=session_id)
            course = Course.objects.get(id=course_id)
            
            # Get all enrollments for this course and session
            enrollments = Enrollment.objects.filter(
                course=course,
                session=session,
                status='active'
            )
            
            updated_count = 0
            for enrollment in enrollments:
                ca_key = f"ca_{enrollment.id}"
                exam_key = f"exam_{enrollment.id}"
                
                ca_score = request.POST.get(ca_key)
                exam_score = request.POST.get(exam_key)
                
                if ca_score and exam_score:
                    result, created = Result.objects.get_or_create(
                        student=enrollment.student,
                        course=course,
                        session=session,
                    )
                    result.continuous_assessment = int(ca_score)
                    result.exam_score = int(exam_score)
                    result.save()
                    updated_count += 1
            
            messages.success(
                request,
                f'Successfully updated {updated_count} results for {course.code}'
            )
            return redirect('school:result_list')
        except Exception as e:
            messages.error(request, f'Error uploading results: {str(e)}')
            return redirect('school:bulk_result_upload')