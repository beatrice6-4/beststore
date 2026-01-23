from django import forms
from django.forms import inlineformset_factory
from .models import Exam, Question, Choice, StudentAnswer


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['title', 'description', 'total_marks', 'passing_marks', 'duration_minutes', 
                  'status', 'is_public', 'allowed_users', 'start_time', 'end_time', 
                  'show_answers', 'allow_review', 'shuffle_questions']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Exam Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Exam Description'
            }),
            'total_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 30
            }),
            'passing_marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 15
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 60
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allowed_users': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'show_answers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'allow_review': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'shuffle_questions': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'difficulty', 'marks', 'order', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Question text'
            }),
            'difficulty': forms.Select(attrs={
                'class': 'form-control'
            }),
            'marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 1
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Explanation (optional)'
            }),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choice text'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class StudentAnswerForm(forms.ModelForm):
    class Meta:
        model = StudentAnswer
        fields = ['selected_choice']
        widgets = {
            'selected_choice': forms.RadioSelect()
        }


# Formsets
ChoiceFormSet = inlineformset_factory(
    Question, Choice, 
    form=ChoiceForm, 
    extra=4, 
    can_delete=True
)

QuestionFormSet = inlineformset_factory(
    Exam, Question,
    form=QuestionForm,
    extra=1,
    can_delete=True
)
