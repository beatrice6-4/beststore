from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Exam(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    total_marks = models.IntegerField(default=30, validators=[MinValueValidator(1)])
    duration_minutes = models.IntegerField(default=60, help_text="Exam duration in minutes")
    passing_marks = models.IntegerField(default=15, validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Access control
    is_public = models.BooleanField(default=True, help_text="Accessible to all users")
    allowed_users = models.ManyToManyField(User, blank=True, related_name='lms_exams', help_text="If set, only these users can access")
    
    # Scheduling
    start_time = models.DateTimeField(help_text="When the exam becomes available")
    end_time = models.DateTimeField(help_text="When the exam closes")
    
    # Exam settings
    show_answers = models.BooleanField(default=True, help_text="Show answers after submission")
    allow_review = models.BooleanField(default=True, help_text="Allow students to review answers")
    shuffle_questions = models.BooleanField(default=False, help_text="Randomize question order")
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_exams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return f"{self.title} ({self.total_marks} marks)"

    def is_available(self):
        """Check if exam is currently available for taking"""
        now = timezone.now()
        return self.status == 'published' and self.start_time <= now <= self.end_time

    def get_question_count(self):
        return self.questions.count()


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(help_text="Question text")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    marks = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    order = models.IntegerField(default=0, help_text="Question order in exam")
    
    explanation = models.TextField(blank=True, help_text="Explanation shown after submission")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['exam', 'order']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}"

    def get_choices(self):
        return self.choices.all().order_by('order')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['question', 'order']
        verbose_name = 'Choice'
        verbose_name_plural = 'Choices'

    def __str__(self):
        return f"{self.question.text[:30]} - {self.text[:50]}"


class ExamAttempt(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_attempts')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    
    # Scoring
    obtained_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    
    # Review
    review_count = models.IntegerField(default=0, help_text="Number of times reviewed")
    last_reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        unique_together = ('exam', 'student')
        verbose_name = 'Exam Attempt'
        verbose_name_plural = 'Exam Attempts'

    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"

    def calculate_score(self):
        """Calculate score based on correct answers"""
        total_marks = 0
        obtained_marks = 0
        
        for answer in self.answers.all():
            if answer.question.marks:
                total_marks += answer.question.marks
                if answer.is_correct():
                    obtained_marks += answer.question.marks
        
        self.obtained_marks = obtained_marks
        if total_marks > 0:
            self.percentage = (obtained_marks / total_marks) * 100
            self.is_passed = self.percentage >= (self.exam.passing_marks / self.exam.total_marks * 100)
        
        self.save()
        return obtained_marks, total_marks

    def get_duration_minutes(self):
        """Get time taken to complete exam"""
        if self.submitted_at:
            duration = self.submitted_at - self.started_at
            return int(duration.total_seconds() / 60)
        return None


class StudentAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attempt', 'question')
        verbose_name = 'Student Answer'
        verbose_name_plural = 'Student Answers'

    def __str__(self):
        return f"{self.attempt.student.username} - Q{self.question.order}"

    def is_correct(self):
        """Check if the selected choice is correct"""
        if self.selected_choice:
            return self.selected_choice.is_correct
        return False
