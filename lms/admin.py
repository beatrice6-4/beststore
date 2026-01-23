from django.contrib import admin
from django.utils.html import format_html
from .models import Exam, Question, Choice, ExamAttempt, StudentAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    fields = ['text', 'is_correct', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'marks', 'difficulty', 'order']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'status_badge', 'total_marks', 'question_count', 'start_time', 'end_time', 'created_by']
    list_filter = ['status', 'created_at', 'is_public']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['allowed_users']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description')
        }),
        ('Exam Details', {
            'fields': ('total_marks', 'passing_marks', 'duration_minutes', 'status')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time')
        }),
        ('Access Control', {
            'fields': ('is_public', 'allowed_users')
        }),
        ('Settings', {
            'fields': ('show_answers', 'allow_review', 'shuffle_questions')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    def status_badge(self, obj):
        colors = {
            'draft': '#FFC107',
            'published': '#28A745',
            'closed': '#DC3545'
        }
        return format_html(
            '<span style="padding: 5px 10px; border-radius: 3px; background-color: {}; color: white;">{}</span>',
            colors.get(obj.status, '#6C757D'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def question_count(self, obj):
        count = obj.get_question_count()
        return format_html('<strong>{}</strong>', count)
    question_count.short_description = 'Questions'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'order', 'text_preview', 'difficulty', 'marks', 'choice_count']
    list_filter = ['exam', 'difficulty', 'created_at']
    search_fields = ['text']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Question', {
            'fields': ('exam', 'text', 'order')
        }),
        ('Details', {
            'fields': ('difficulty', 'marks', 'explanation')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ChoiceInline]
    
    def text_preview(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Question'
    
    def choice_count(self, obj):
        count = obj.choices.count()
        return format_html('<strong>{}</strong> choices', count)
    choice_count.short_description = 'Choices'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'text_preview', 'is_correct_badge', 'order']
    list_filter = ['is_correct', 'created_at']
    search_fields = ['text', 'question__text']
    
    def text_preview(self, obj):
        return obj.text[:60] + '...' if len(obj.text) > 60 else obj.text
    text_preview.short_description = 'Choice Text'
    
    def is_correct_badge(self, obj):
        if obj.is_correct:
            return format_html('<span style="color: green; font-weight: bold;">✓ Correct</span>')
        return format_html('<span style="color: red;">✗ Incorrect</span>')
    is_correct_badge.short_description = 'Correct'


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'exam', 'status_badge', 'obtained_marks', 'percentage_badge', 'started_at']
    list_filter = ['status', 'is_passed', 'started_at']
    search_fields = ['student__username', 'exam__title']
    readonly_fields = ['started_at', 'submitted_at', 'obtained_marks', 'percentage', 'is_passed']
    
    fieldsets = (
        ('Attempt Information', {
            'fields': ('exam', 'student', 'status')
        }),
        ('Results', {
            'fields': ('obtained_marks', 'percentage', 'is_passed')
        }),
        ('Timing', {
            'fields': ('started_at', 'submitted_at')
        }),
        ('Review', {
            'fields': ('review_count', 'last_reviewed_at')
        }),
    )
    
    def student_name(self, obj):
        return obj.student.get_full_name() or obj.student.username
    student_name.short_description = 'Student'
    
    def status_badge(self, obj):
        colors = {
            'in_progress': '#007BFF',
            'submitted': '#FFC107',
            'completed': '#28A745'
        }
        return format_html(
            '<span style="padding: 5px 10px; border-radius: 3px; background-color: {}; color: white;">{}</span>',
            colors.get(obj.status, '#6C757D'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def percentage_badge(self, obj):
        if obj.percentage is None:
            return '-'
        color = 'green' if obj.is_passed else 'red'
        percentage_str = f"{obj.percentage:.2f}"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}%</span>',
            color,
            percentage_str
        )
    percentage_badge.short_description = 'Score %'


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'selected_choice_text', 'is_correct_badge']
    list_filter = ['attempt__exam', 'answered_at']
    search_fields = ['attempt__student__username', 'question__text']
    readonly_fields = ['answered_at', 'updated_at']
    
    def selected_choice_text(self, obj):
        return obj.selected_choice.text if obj.selected_choice else 'Not answered'
    selected_choice_text.short_description = 'Selected Answer'
    
    def is_correct_badge(self, obj):
        if obj.selected_choice is None:
            return format_html('<span style="color: gray;">Not answered</span>')
        if obj.is_correct():
            return format_html('<span style="color: green; font-weight: bold;">✓ Correct</span>')
        return format_html('<span style="color: red;">✗ Incorrect</span>')
    is_correct_badge.short_description = 'Correct'
