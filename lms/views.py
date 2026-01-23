from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Exam, Question, ExamAttempt, StudentAnswer, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm, StudentAnswerForm, ChoiceFormSet, QuestionFormSet
import json


def is_staff(user):
    """Check if user is staff/admin"""
    return user.is_authenticated and user.is_staff


# ============= ADMIN VIEWS =============

@login_required
@user_passes_test(is_staff)
def admin_dashboard(request):
    """Admin LMS Dashboard"""
    exams = Exam.objects.filter(created_by=request.user)
    total_exams = exams.count()
    total_attempts = ExamAttempt.objects.filter(exam__created_by=request.user).count()
    
    context = {
        'exams': exams[:5],  # Latest 5 exams
        'total_exams': total_exams,
        'total_attempts': total_attempts,
    }
    return render(request, 'lms/admin/dashboard.html', context)


@login_required
@user_passes_test(is_staff)
def create_exam(request):
    """Create a new exam"""
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.created_by = request.user
            exam.save()
            form.save_m2m()
            messages.success(request, 'Exam created successfully!')
            return redirect('lms:edit_exam', pk=exam.pk)
    else:
        form = ExamForm()
    
    context = {'form': form, 'title': 'Create New Exam'}
    return render(request, 'lms/admin/exam_form.html', context)


@login_required
@user_passes_test(is_staff)
def edit_exam(request, pk):
    """Edit exam details"""
    exam = get_object_or_404(Exam, pk=pk, created_by=request.user)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated successfully!')
            return redirect('lms:exam_detail', pk=exam.pk)
    else:
        form = ExamForm(instance=exam)
    
    context = {
        'form': form,
        'exam': exam,
        'title': f'Edit: {exam.title}'
    }
    return render(request, 'lms/admin/exam_form.html', context)


@login_required
@user_passes_test(is_staff)
def exam_detail(request, pk):
    """View exam details with questions"""
    exam = get_object_or_404(Exam, pk=pk, created_by=request.user)
    questions = exam.questions.all().order_by('order')
    attempts = exam.attempts.all().count()
    
    context = {
        'exam': exam,
        'questions': questions,
        'attempts': attempts,
    }
    return render(request, 'lms/admin/exam_detail.html', context)


@login_required
@user_passes_test(is_staff)
def create_question(request, exam_pk):
    """Create a new question"""
    exam = get_object_or_404(Exam, pk=exam_pk, created_by=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            messages.success(request, 'Question created! Now add choices.')
            return redirect('lms:add_choices', question_pk=question.pk)
    else:
        form = QuestionForm()
    
    context = {
        'form': form,
        'exam': exam,
        'title': 'Add Question'
    }
    return render(request, 'lms/admin/question_form.html', context)


@login_required
@user_passes_test(is_staff)
def add_choices(request, question_pk):
    """Add multiple choice options to a question"""
    question = get_object_or_404(Question, pk=question_pk, exam__created_by=request.user)
    
    if request.method == 'POST':
        formset = ChoiceFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            
            # Validate at least one correct answer
            if not question.choices.filter(is_correct=True).exists():
                messages.error(request, 'Please mark at least one choice as correct!')
                return redirect('lms:add_choices', question_pk=question.pk)
            
            messages.success(request, 'Choices saved successfully!')
            return redirect('lms:exam_detail', pk=question.exam.pk)
    else:
        formset = ChoiceFormSet(instance=question)
    
    context = {
        'formset': formset,
        'question': question,
        'exam': question.exam,
        'title': 'Add Answer Choices'
    }
    return render(request, 'lms/admin/add_choices.html', context)


@login_required
@user_passes_test(is_staff)
def edit_question(request, question_pk):
    """Edit a question"""
    question = get_object_or_404(Question, pk=question_pk, exam__created_by=request.user)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated!')
            return redirect('lms:add_choices', question_pk=question.pk)
    else:
        form = QuestionForm(instance=question)
    
    context = {
        'form': form,
        'question': question,
        'title': 'Edit Question'
    }
    return render(request, 'lms/admin/question_form.html', context)


@login_required
@user_passes_test(is_staff)
def exam_results(request, exam_pk):
    """View all exam results"""
    exam = get_object_or_404(Exam, pk=exam_pk, created_by=request.user)
    attempts = exam.attempts.all().order_by('-started_at')
    
    context = {
        'exam': exam,
        'attempts': attempts,
    }
    return render(request, 'lms/admin/exam_results.html', context)


@login_required
@user_passes_test(is_staff)
def student_exam_details(request, attempt_pk):
    """View detailed results for a student's exam attempt"""
    attempt = get_object_or_404(ExamAttempt, pk=attempt_pk, exam__created_by=request.user)
    answers = attempt.answers.all().select_related('selected_choice', 'question')
    
    context = {
        'attempt': attempt,
        'answers': answers,
    }
    return render(request, 'lms/admin/student_exam_details.html', context)


# ============= STUDENT VIEWS =============

@login_required
def exam_list(request):
    """List all available exams for students"""
    now = timezone.now()
    
    # Get available exams
    exams = Exam.objects.filter(
        Q(is_public=True) | Q(allowed_users=request.user),
        status='published'
    ).distinct().order_by('-start_time')
    
    # Get student's attempts
    attempts = ExamAttempt.objects.filter(student=request.user)
    
    context = {
        'exams': exams,
        'attempts': attempts,
    }
    return render(request, 'lms/student/exam_list.html', context)


@login_required
def exam_instructions(request, exam_pk):
    """Show exam instructions before starting"""
    exam = get_object_or_404(Exam, pk=exam_pk)
    
    # Check if user can take exam
    if not exam.is_public and request.user not in exam.allowed_users.all():
        messages.error(request, 'You do not have access to this exam.')
        return redirect('lms:exam_list')
    
    if not exam.is_available():
        messages.error(request, 'This exam is not currently available.')
        return redirect('lms:exam_list')
    
    # Check if already attempted
    attempt = ExamAttempt.objects.filter(exam=exam, student=request.user).first()
    
    if request.method == 'POST':
        # Create new attempt or continue existing one
        if not attempt:
            attempt = ExamAttempt.objects.create(exam=exam, student=request.user)
        return redirect('lms:take_exam', attempt_pk=attempt.pk)
    
    context = {
        'exam': exam,
        'attempt': attempt,
    }
    return render(request, 'lms/student/exam_instructions.html', context)


@login_required
def take_exam(request, attempt_pk):
    """Take the exam - answer questions"""
    attempt = get_object_or_404(ExamAttempt, pk=attempt_pk, student=request.user)
    exam = attempt.exam
    
    # Check if exam is still available
    if not exam.is_available():
        messages.error(request, 'This exam is no longer available.')
        return redirect('lms:exam_list')
    
    # Check if already submitted
    if attempt.status != 'in_progress':
        messages.info(request, 'You have already submitted this exam.')
        return redirect('lms:exam_result', attempt_pk=attempt.pk)
    
    questions = exam.questions.all().order_by('order')
    
    if request.method == 'POST':
        # Save answers
        for question in questions:
            choice_id = request.POST.get(f'question_{question.id}')
            
            answer, created = StudentAnswer.objects.get_or_create(
                attempt=attempt,
                question=question
            )
            
            if choice_id:
                choice = Choice.objects.get(id=choice_id)
                answer.selected_choice = choice
                answer.save()
            elif not created:
                # Remove answer if no choice selected
                answer.delete()
        
        # Mark as submitted
        attempt.status = 'submitted'
        attempt.submitted_at = timezone.now()
        attempt.save()
        
        # Calculate score
        attempt.calculate_score()
        
        messages.success(request, 'Exam submitted successfully!')
        return redirect('lms:exam_result', attempt_pk=attempt.pk)
    
    context = {
        'exam': exam,
        'attempt': attempt,
        'questions': questions,
        'total_questions': questions.count(),
    }
    return render(request, 'lms/student/take_exam.html', context)


@login_required
def exam_result(request, attempt_pk):
    """View exam results"""
    attempt = get_object_or_404(ExamAttempt, pk=attempt_pk, student=request.user)
    exam = attempt.exam
    
    if attempt.status == 'in_progress':
        messages.info(request, 'You must submit the exam first.')
        return redirect('lms:take_exam', attempt_pk=attempt.pk)
    
    # Get answers
    answers = attempt.answers.all().select_related('question', 'selected_choice')
    
    # Mark as completed (only once)
    if attempt.status == 'submitted':
        attempt.status = 'completed'
        attempt.save()
    
    # Increment review count
    if request.GET.get('review') == '1':
        attempt.review_count += 1
        attempt.last_reviewed_at = timezone.now()
        attempt.save()
    
    context = {
        'exam': exam,
        'attempt': attempt,
        'answers': answers,
        'show_answers': exam.show_answers,
        'allow_review': exam.allow_review,
    }
    return render(request, 'lms/student/exam_result.html', context)


@login_required
def my_exams(request):
    """View student's exam history"""
    attempts = ExamAttempt.objects.filter(student=request.user).select_related('exam').order_by('-started_at')
    
    context = {
        'attempts': attempts,
    }
    return render(request, 'lms/student/my_exams.html', context)


# ============= API VIEWS =============

@login_required
@require_http_methods(["POST"])
def save_answer_ajax(request, attempt_pk, question_id):
    """AJAX endpoint to save answer"""
    attempt = get_object_or_404(ExamAttempt, pk=attempt_pk, student=request.user)
    question = get_object_or_404(Question, id=question_id)
    
    try:
        data = json.loads(request.body)
        choice_id = data.get('choice_id')
        
        answer, created = StudentAnswer.objects.get_or_create(
            attempt=attempt,
            question=question
        )
        
        if choice_id:
            choice = Choice.objects.get(id=choice_id)
            answer.selected_choice = choice
            answer.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_exam_time_remaining(request, attempt_pk):
    """Get remaining time for exam"""
    attempt = get_object_or_404(ExamAttempt, pk=attempt_pk, student=request.user)
    exam = attempt.exam
    
    now = timezone.now()
    time_remaining = (exam.end_time - now).total_seconds()
    
    if time_remaining < 0:
        time_remaining = 0
    
    return JsonResponse({
        'time_remaining': int(time_remaining),
        'exam_duration': exam.duration_minutes * 60,
    })
