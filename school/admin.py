from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Course, ReportingSession, Student, Enrollment, StudentFee, Result

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name_display', 'code_display', 'head_display', 'status_display')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Department Information', {
            'fields': ('name', 'code', 'description', 'head_of_department')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def name_display(self, obj):
        return format_html(
            '<strong style="color:#1f3a5f;">{}</strong>',
            obj.name
        )
    name_display.short_description = 'Department'

    def code_display(self, obj):
        return format_html(
            '<span style="background:#e8f4f8; padding:4px 12px; border-radius:4px; color:#2980b9; font-weight:bold;">{}</span>',
            obj.code
        )
    code_display.short_description = 'Code'

    def head_display(self, obj):
        return obj.head_of_department or 'Not Assigned'

    def status_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#d1fae5; color:#065f46; padding:4px 12px; border-radius:4px; font-weight:bold;">'
                '<i class="fas fa-check-circle"></i> Active</span>'
            )
        return format_html(
            '<span style="background:#fee2e2; color:#991b1b; padding:4px 12px; border-radius:4px; font-weight:bold;">'
            '<i class="fas fa-times-circle"></i> Inactive</span>'
        )
    status_display.short_description = 'Status'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code_display', 'name_display', 'department_display', 'credits_display', 'lecturer_display', 'status_display')
    search_fields = ('name', 'code', 'department__name')
    list_filter = ('department', 'is_active')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Course Information', {
            'fields': ('name', 'code', 'department', 'credits', 'lecturer')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def code_display(self, obj):
        return format_html(
            '<strong style="color:#6366f1; font-family:monospace;">{}</strong>',
            obj.code
        )
    code_display.short_description = 'Course Code'

    def name_display(self, obj):
        return obj.name[:50] + '...' if len(obj.name) > 50 else obj.name

    def department_display(self, obj):
        return format_html(
            '<span style="background:#fef3c7; color:#92400e; padding:4px 12px; border-radius:4px; font-weight:bold;">{}</span>',
            obj.department.name
        )
    department_display.short_description = 'Department'

    def credits_display(self, obj):
        return format_html(
            '<span style="background:#e0e7ff; color:#4f46e5; padding:4px 12px; border-radius:4px; font-weight:bold;">{} Credits</span>',
            obj.credits
        )
    credits_display.short_description = 'Credits'

    def lecturer_display(self, obj):
        return obj.lecturer or 'Not Assigned'

    def status_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#d1fae5; color:#065f46; padding:4px 12px; border-radius:4px; font-weight:bold;">'
                '<i class="fas fa-check-circle"></i> Active</span>'
            )
        return format_html(
            '<span style="background:#fee2e2; color:#991b1b; padding:4px 12px; border-radius:4px; font-weight:bold;">'
            '<i class="fas fa-times-circle"></i> Inactive</span>'
        )
    status_display.short_description = 'Status'


@admin.register(ReportingSession)
class ReportingSessionAdmin(admin.ModelAdmin):
    list_display = ('name_display', 'semester_display', 'date_range_display', 'current_display', 'status_display')
    search_fields = ('name',)
    list_filter = ('is_current', 'is_active', 'semester')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Session Information', {
            'fields': ('name', 'semester', 'start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_current', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def name_display(self, obj):
        return format_html(
            '<strong style="color:#1f3a5f;">{}</strong>',
            obj.name
        )
    name_display.short_description = 'Session'

    def semester_display(self, obj):
        sem_colors = {'1': '#e0e7ff', '2': '#fce7f3', '3': '#dcfce7'}
        sem_color_text = {'1': '#4f46e5', '2': '#be185d', '3': '#15803d'}
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 12px; border-radius:4px; font-weight:bold;">{}</span>',
            sem_colors.get(obj.semester, '#e5e7eb'),
            sem_color_text.get(obj.semester, '#6b7280'),
            obj.get_semester_display()
        )
    semester_display.short_description = 'Semester'

    def date_range_display(self, obj):
        return format_html(
            '<i class="fas fa-calendar"></i> {} - {}',
            obj.start_date.strftime('%d %b %Y'),
            obj.end_date.strftime('%d %b %Y')
        )
    date_range_display.short_description = 'Date Range'

    def current_display(self, obj):
        if obj.is_current:
            return format_html(
                '<span style="background:#d1fae5; color:#065f46; padding:4px 12px; border-radius:4px; font-weight:bold;">'
                '<i class="fas fa-star"></i> Current</span>'
            )
        return '—'
    current_display.short_description = 'Current'

    def status_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background:#d1fae5; color:#065f46; padding:4px 12px; border-radius:4px;">'
                '<i class="fas fa-check-circle"></i> Active</span>'
            )
        return format_html(
            '<span style="background:#fee2e2; color:#991b1b; padding:4px 12px; border-radius:4px;">'
            '<i class="fas fa-times-circle"></i> Inactive</span>'
        )
    status_display.short_description = 'Status'


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('reg_number_display', 'name_display', 'email_display', 'department_display', 'status_display')
    search_fields = ('registration_number', 'first_name', 'last_name', 'email')
    list_filter = ('department', 'status', 'admission_date')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Student Information', {
            'fields': ('registration_number', 'first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Personal Details', {
            'fields': ('date_of_birth', 'gender', 'address')
        }),
        ('Academic Information', {
            'fields': ('department', 'admission_date', 'status')
        }),
        ('Guardian Information', {
            'fields': ('guardian_name', 'guardian_phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def reg_number_display(self, obj):
        return format_html(
            '<strong style="color:#6366f1; font-family:monospace;">{}</strong>',
            obj.registration_number
        )
    reg_number_display.short_description = 'Reg. No.'

    def name_display(self, obj):
        return obj.get_full_name()

    def email_display(self, obj):
        return format_html(
            '<i class="fas fa-envelope"></i> {}',
            obj.email
        )
    email_display.short_description = 'Email'

    def department_display(self, obj):
        return format_html(
            '<span style="background:#fef3c7; color:#92400e; padding:4px 12px; border-radius:4px; font-weight:bold;">{}</span>',
            obj.department.name
        )
    department_display.short_description = 'Department'

    def status_display(self, obj):
        status_colors = {
            'active': '#d1fae5',
            'inactive': '#fee2e2',
            'suspended': '#fef3c7',
            'graduated': '#dbeafe'
        }
        status_text_colors = {
            'active': '#065f46',
            'inactive': '#991b1b',
            'suspended': '#92400e',
            'graduated': '#0c4a6e'
        }
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 12px; border-radius:4px; font-weight:bold;">'
            '<i class="fas fa-user-check"></i> {}</span>',
            status_colors.get(obj.status, '#e5e7eb'),
            status_text_colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'course_display', 'session_display', 'status_display')
    search_fields = ('student__registration_number', 'course__code')
    list_filter = ('session', 'status', 'enrollment_date')
    readonly_fields = ('enrollment_date', 'updated_at')

    fieldsets = (
        ('Enrollment Information', {
            'fields': ('student', 'course', 'session', 'status')
        }),
        ('Timestamps', {
            'fields': ('enrollment_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def student_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">{}</small>',
            obj.student.get_full_name(),
            obj.student.registration_number
        )
    student_display.short_description = 'Student'

    def course_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">{}</small>',
            obj.course.name,
            obj.course.code
        )
    course_display.short_description = 'Course'

    def session_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">Semester {}</small>',
            obj.session.name,
            obj.session.semester
        )
    session_display.short_description = 'Session'

    def status_display(self, obj):
        status_colors = {
            'enrolled': '#d1fae5',
            'dropped': '#fee2e2',
            'completed': '#dbeafe'
        }
        status_text_colors = {
            'enrolled': '#065f46',
            'dropped': '#991b1b',
            'completed': '#0c4a6e'
        }
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 12px; border-radius:4px; font-weight:bold;">{}</span>',
            status_colors.get(obj.status, '#e5e7eb'),
            status_text_colors.get(obj.status, '#6b7280'),
            obj.get_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'fee_type_display', 'amount_display', 'paid_display', 'balance_display', 'status_display')
    search_fields = ('student__registration_number', 'student__first_name', 'student__last_name')
    list_filter = ('fee_type', 'payment_status', 'session')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Fee Information', {
            'fields': ('student', 'session', 'fee_type', 'amount')
        }),
        ('Payment Details', {
            'fields': ('paid_amount', 'payment_status', 'payment_date', 'due_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def student_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">{}</small>',
            obj.student.get_full_name(),
            obj.student.registration_number
        )
    student_display.short_description = 'Student'

    def fee_type_display(self, obj):
        return obj.get_fee_type_display()
    fee_type_display.short_description = 'Fee Type'

    def amount_display(self, obj):
        return format_html(
            '<span style="color:#27ae60; font-weight:bold;">Ksh {:,.2f}</span>',
            obj.amount
        )
    amount_display.short_description = 'Amount'

    def paid_display(self, obj):
        return format_html(
            '<span style="color:#2980b9; font-weight:bold;">Ksh {:,.2f}</span>',
            obj.paid_amount
        )
    paid_display.short_description = 'Paid'

    def balance_display(self, obj):
        balance = obj.balance
        color = '#27ae60' if balance == 0 else '#e74c3c'
        return format_html(
            '<span style="color:{}; font-weight:bold;">Ksh {:,.2f}</span>',
            color,
            balance
        )
    balance_display.short_description = 'Balance'

    def status_display(self, obj):
        status_colors = {
            'unpaid': '#fee2e2',
            'partial': '#fef3c7',
            'paid': '#d1fae5'
        }
        status_text_colors = {
            'unpaid': '#991b1b',
            'partial': '#92400e',
            'paid': '#065f46'
        }
        return format_html(
            '<span style="background:{}; color:{}; padding:4px 12px; border-radius:4px; font-weight:bold;">{}</span>',
            status_colors.get(obj.payment_status, '#e5e7eb'),
            status_text_colors.get(obj.payment_status, '#6b7280'),
            obj.get_payment_status_display()
        )
    status_display.short_description = 'Status'


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student_display', 'course_display', 'session_display', 'score_display', 'grade_display', 'pass_display')
    search_fields = ('student__registration_number', 'course__code')
    list_filter = ('grade', 'is_pass', 'session')
    readonly_fields = ('total_score', 'grade', 'grade_point', 'is_pass', 'recorded_date', 'updated_date')

    fieldsets = (
        ('Result Information', {
            'fields': ('student', 'course', 'session')
        }),
        ('Scores', {
            'fields': ('continuous_assessment', 'exam_score', 'total_score')
        }),
        ('Grade Details', {
            'fields': ('grade', 'grade_point', 'is_pass')
        }),
        ('Timestamps', {
            'fields': ('recorded_date', 'updated_date'),
            'classes': ('collapse',)
        }),
    )

    def student_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">{}</small>',
            obj.student.get_full_name(),
            obj.student.registration_number
        )
    student_display.short_description = 'Student'

    def course_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">{}</small>',
            obj.course.name,
            obj.course.code
        )
    course_display.short_description = 'Course'

    def session_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small style="color:#6b7280;">Semester {}</small>',
            obj.session.name,
            obj.session.semester
        )
    session_display.short_description = 'Session'

    def score_display(self, obj):
        return format_html(
            '<strong>{}/100</strong><br><small style="color:#6b7280;">CA: {}/40 | Exam: {}/60</small>',
            obj.total_score,
            obj.continuous_assessment,
            obj.exam_score
        )
    score_display.short_description = 'Score'

    def grade_display(self, obj):
        grade_colors = {
            'A+': '#10b981', 'A': '#10b981', 'B+': '#3b82f6', 'B': '#3b82f6',
            'C+': '#f59e0b', 'C': '#f59e0b', 'D': '#ef4444', 'F': '#ef4444'
        }
        return format_html(
            '<span style="background:{}; color:white; padding:8px 16px; border-radius:6px; font-weight:bold; font-size:1.1rem;">'
            '{} (GP: {})</span>',
            grade_colors.get(obj.grade, '#6b7280'),
            obj.grade,
            obj.grade_point
        )
    grade_display.short_description = 'Grade'

    def pass_display(self, obj):
        if obj.is_pass:
            return format_html(
                '<span style="background:#d1fae5; color:#065f46; padding:4px 12px; border-radius:4px; font-weight:bold;">'
                '<i class="fas fa-check-circle"></i> Pass</span>'
            )
        return format_html(
            '<span style="background:#fee2e2; color:#991b1b; padding:4px 12px; border-radius:4px; font-weight:bold;">'
            '<i class="fas fa-times-circle"></i> Fail</span>'
        )
    pass_display.short_description = 'Status'