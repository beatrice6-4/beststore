from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


class Department(models.Model):
    """School departments"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)
    head_of_department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Departments'

    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    """School courses"""
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(12)])
    lecturer = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']
        unique_together = ['code', 'department']

    def __str__(self):
        return f"{self.code} - {self.name}"


class ReportingSession(models.Model):
    """Academic sessions/terms"""
    SEMESTER_CHOICES = [
        ('1', 'First Semester'),
        ('2', 'Second Semester'),
        ('3', 'Third Semester'),
    ]

    name = models.CharField(max_length=50)  # e.g., "2024/2025"
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['name', 'semester']

    def __str__(self):
        return f"{self.name} - Semester {self.semester}"


class Session(models.Model):
    """Academic Session/Term model"""
    name = models.CharField(max_length=50, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'

    def __str__(self):
        return self.name

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date.')

    @property
    def status(self):
        """Get session status: active, upcoming, or closed"""
        today = timezone.now().date()
        
        if self.start_date <= today <= self.end_date:
            return 'active'
        elif self.start_date > today:
            return 'upcoming'
        else:
            return 'closed'

    @property
    def get_status_display(self):
        status_map = {
            'active': 'Active',
            'upcoming': 'Upcoming',
            'closed': 'Closed'
        }
        return status_map.get(self.status, 'Unknown')

    @property
    def duration_days(self):
        """Get total duration in days"""
        return (self.end_date - self.start_date).days


class Student(models.Model):
    """Student profile"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
    ]

    registration_number = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='students')
    admission_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    courses = models.ManyToManyField(Course, related_name='enrolled_students', through='Enrollment')
    address = models.TextField(blank=True, null=True)
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['registration_number']

    def __str__(self):
        return f"{self.registration_number} - {self.get_full_name()}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Enrollment(models.Model):
    """Student course enrollment"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
    ]
    
    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments_list')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='course_enrollments')
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    grade = models.CharField(max_length=1, choices=GRADE_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ('student', 'course', 'session')

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.name}"

    def clean(self):
        if Enrollment.objects.filter(
            student=self.student, 
            course=self.course,
            session=self.session
        ).exclude(id=self.id).exists():
            raise ValidationError("This student is already enrolled in this course for this session.")


class StudentFee(models.Model):
    """Student fee records"""
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition'),
        ('lab', 'Laboratory'),
        ('library', 'Library'),
        ('registration', 'Registration'),
        ('activity', 'Activity'),
        ('other', 'Other'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    session = models.ForeignKey(ReportingSession, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
    due_date = models.DateField()
    payment_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['student', 'session', 'fee_type']

    def __str__(self):
        return f"{self.student.registration_number} - {self.fee_type} - {self.session}"

    @property
    def balance(self):
        return self.amount - self.paid_amount


class Result(models.Model):
    """Student course results"""
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'),
        ('A', 'A (80-89)'),
        ('B+', 'B+ (70-79)'),
        ('B', 'B (60-69)'),
        ('C+', 'C+ (50-59)'),
        ('C', 'C (40-49)'),
        ('D', 'D (30-39)'),
        ('F', 'F (0-29)'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='results')
    session = models.ForeignKey(ReportingSession, on_delete=models.CASCADE, related_name='results')
    continuous_assessment = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(40)],
        help_text="Out of 40"
    )
    exam_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(60)],
        help_text="Out of 60"
    )
    total_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        editable=False
    )
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, editable=False)
    grade_point = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(4)],
        editable=False
    )
    is_pass = models.BooleanField(default=True, editable=False)
    recorded_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-recorded_date']
        unique_together = ['student', 'course', 'session']

    def __str__(self):
        return f"{self.student.registration_number} - {self.course.code} - {self.grade}"

    def save(self, *args, **kwargs):
        # Calculate total score
        self.total_score = self.continuous_assessment + self.exam_score

        # Assign grade
        if self.total_score >= 90:
            self.grade = 'A+'
            self.grade_point = 4.0
        elif self.total_score >= 80:
            self.grade = 'A'
            self.grade_point = 3.9
        elif self.total_score >= 70:
            self.grade = 'B+'
            self.grade_point = 3.7
        elif self.total_score >= 60:
            self.grade = 'B'
            self.grade_point = 3.0
        elif self.total_score >= 50:
            self.grade = 'C+'
            self.grade_point = 2.3
        elif self.total_score >= 40:
            self.grade = 'C'
            self.grade_point = 2.0
        elif self.total_score >= 30:
            self.grade = 'D'
            self.grade_point = 1.0
        else:
            self.grade = 'F'
            self.grade_point = 0.0

        self.is_pass = self.total_score >= 40

        super().save(*args, **kwargs)