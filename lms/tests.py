from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Exam, Question, Choice, ExamAttempt, StudentAnswer
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class ExamModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.admin_user = User.objects.create_user(username='admin', password='pass123', is_staff=True)
        
        self.exam = Exam.objects.create(
            title='Test Exam',
            description='A test exam',
            total_marks=30,
            passing_marks=15,
            duration_minutes=60,
            status='published',
            created_by=self.admin_user,
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=2)
        )
    
    def test_exam_creation(self):
        self.assertEqual(self.exam.title, 'Test Exam')
        self.assertEqual(self.exam.total_marks, 30)
        self.assertTrue(self.exam.is_available())
    
    def test_question_creation(self):
        question = Question.objects.create(
            exam=self.exam,
            text='What is 2 + 2?',
            marks=1,
            order=1
        )
        self.assertEqual(question.exam, self.exam)
        self.assertEqual(self.exam.get_question_count(), 1)
    
    def test_exam_attempt_calculation(self):
        question = Question.objects.create(
            exam=self.exam,
            text='Test Question',
            marks=5,
            order=1
        )
        
        correct_choice = Choice.objects.create(
            question=question,
            text='Correct',
            is_correct=True,
            order=1
        )
        
        incorrect_choice = Choice.objects.create(
            question=question,
            text='Incorrect',
            is_correct=False,
            order=2
        )
        
        attempt = ExamAttempt.objects.create(
            exam=self.exam,
            student=self.user
        )
        
        # Add a correct answer
        StudentAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_choice=correct_choice
        )
        
        attempt.calculate_score()
        self.assertEqual(attempt.obtained_marks, 5)
        self.assertEqual(attempt.percentage, 100.0 / 30 * 5)
