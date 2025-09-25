from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Group, Payment, Activity, Training, Service
from django import forms
from django.db.models import Sum
from datetime import datetime
from collections import defaultdict
from django.contrib.auth.mixins import UserPassesTestMixin

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
class PaymentListView(UserPassesTestMixin, ListView):
    model = Payment
    template_name = 'CDMIS/payment_list.html'
    context_object_name = 'payments'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_payments = Payment.objects.all().order_by('payment_date')
        context['total_amount'] = all_payments.aggregate(total=Sum('amount'))['total'] or 0

        # Group payments by date and sum amounts
        from collections import defaultdict
        payments_by_date = defaultdict(list)
        for payment in all_payments:
            payments_by_date[payment.payment_date].append(payment)

        grouped_payments = []
        for date, payments in payments_by_date.items():
            date_total = sum(p.amount for p in payments)
            grouped_payments.append({
                'date': date,
                'payments': payments,
                'date_total': date_total
            })

        grouped_payments.sort(key=lambda x: x['date'])
        context['grouped_payments'] = grouped_payments
        return context

class PaymentCreateView(UserPassesTestMixin, CreateView):
    model = Payment
    form_class = PaymentForm
    template_name = 'CDMIS/payment_form.html'
    success_url = reverse_lazy('cdmis:payment_list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You do not have permission to view this page.")

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