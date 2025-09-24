from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Group, Payment, Activity, Training, Service
from django import forms

# --- Forms ---
class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'registration_date', 'description']

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['group', 'amount', 'payment_date', 'notes']

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['group', 'title', 'activity_date', 'description']

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        fields = ['group', 'topic', 'trainer', 'training_date', 'notes']

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['group', 'name', 'service_date', 'description']

# --- Group Views ---
class GroupListView(ListView):
    model = Group
    template_name = 'CDMIS/group_list.html'
    context_object_name = 'groups'

class GroupDetailView(DetailView):
    model = Group
    template_name = 'CDMIS/group_detail.html'
    context_object_name = 'group'

class GroupCreateView(CreateView):
    model = Group
    form_class = GroupForm
    template_name = 'CDMIS/group_form.html'
    success_url = reverse_lazy('cdmis:group_list')

# --- Payment Views ---
class PaymentListView(ListView):
    model = Payment
    template_name = 'CDMIS/payment_list.html'
    context_object_name = 'payments'

class PaymentCreateView(CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'CDMIS/payment_form.html'
    success_url = reverse_lazy('cdmis:payment_list')

# --- Activity Views ---
class ActivityListView(ListView):
    model = Activity
    template_name = 'CDMIS/activity_list.html'
    context_object_name = 'activities'

class ActivityCreateView(CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'CDMIS/activity_form.html'
    success_url = reverse_lazy('cdmis:activity_list')

# --- Training Views ---
class TrainingListView(ListView):
    model = Training
    template_name = 'CDMIS/training_list.html'
    context_object_name = 'trainings'

class TrainingCreateView(CreateView):
    model = Training
    form_class = TrainingForm
    template_name = 'CDMIS/training_form.html'
    success_url = reverse_lazy('cdmis:training_list')

# --- Service Views ---
class ServiceListView(ListView):
    model = Service
    template_name = 'CDMIS/service_list.html'
    context_object_name = 'services'

class ServiceCreateView(CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'CDMIS/service_form.html'
    success_url = reverse_lazy('cdmis:service_list')