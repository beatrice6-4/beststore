from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from .models import Group, Payment, Activity, Training, Service
from django import forms
from django.db.models import Sum
from django.views import View
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



from django.views.generic import UpdateView, DeleteView

class GroupUpdateView(UserPassesTestMixin, UpdateView):
    model = Group
    form_class = GroupForm
    template_name = 'CDMIS/group_form.html'
    success_url = reverse_lazy('cdmis:group_list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

class GroupDeleteView(UserPassesTestMixin, DeleteView):
    model = Group
    template_name = 'CDMIS/group_confirm_delete.html'
    success_url = reverse_lazy('cdmis:group_list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")




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
from django.shortcuts import render
from django.views.generic import ListView
from .models import Payment
from django.db.models import Sum
from collections import defaultdict
from django.contrib.auth.mixins import UserPassesTestMixin

class PaymentListView(UserPassesTestMixin, ListView):
    model = Payment
    template_name = 'CDMIS/payment_list.html'
    context_object_name = 'payments'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_payments = Payment.objects.all().order_by('payment_date')
        context['all_payments'] = all_payments

        # Calculate totals per date
        date_totals = defaultdict(int)
        for payment in all_payments:
            date_totals[payment.payment_date] += payment.amount
        context['date_totals'] = date_totals

        # Group payments by date for easy template rendering
        payments_by_date = defaultdict(list)
        for payment in all_payments:
            payments_by_date[payment.payment_date].append(payment)
        # Create a sorted list of (date, payments) tuples
        context['payments_by_date'] = sorted(payments_by_date.items())

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
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

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




class FinanceView(UserPassesTestMixin, View):
    template_name = 'CDMIS/finance.html'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

    def get(self, request, *args, **kwargs):
        from collections import defaultdict
        from .models import Group, Payment

        # Fetch all payments, group by date
        payments = Payment.objects.select_related('group').order_by('payment_date')
        finance_data = defaultdict(list)
        for payment in payments:
            finance_data[payment.payment_date].append({
                'group': payment.group.name,
                'amount': payment.amount
            })

        # Prepare list for template: [{date, payments: [{group, amount}], date_total}]
        finance_list = []
        for date, items in finance_data.items():
            date_total = sum(item['amount'] for item in items)
            finance_list.append({
                'date': date,
                'payments': items,
                'date_total': date_total
            })
        finance_list.sort(key=lambda x: x['date'])

        # Grand total
        grand_total = payments.aggregate(total=Sum('amount'))['total'] or 0

        return render(request, self.template_name, {
            'finance_list': finance_list,
            'grand_total': grand_total,
        })
    




from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

class UserListView(UserPassesTestMixin, ListView):
    model = User
    template_name = 'CDMIS/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inactive_users'] = User.objects.filter(is_active=False).order_by('-date_joined')
        context['active_users'] = User.objects.filter(is_active=True).order_by('-date_joined')
        return context

class UserUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff']
    template_name = 'CDMIS/user_form.html'
    success_url = reverse_lazy('cdmis:user_list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

class UserDeleteView(UserPassesTestMixin, DeleteView):
    model = User
    template_name = 'CDMIS/user_confirm_delete.html'
    success_url = reverse_lazy('cdmis:user_list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")

def activate_user(request, pk):
    if not (request.user.is_staff or request.user.is_superuser):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("ERROR 404, ONLY ADMINS ARE ALLOWED TO VIEW THIS PAGE.")
    user = get_object_or_404(User, pk=pk)
    user.is_active = True
    user.save()
    messages.success(request, f"User {user.username} activated.")
    return redirect('cdmis:user_list')

from django.http import HttpResponse
from .models import Payment
import csv

def download_payments_by_date(request, date):
    # date is expected as 'YYYY-MM-DD'
    payments = Payment.objects.filter(payment_date=date)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payments_{date}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Group', 'Amount', 'Date', 'Notes'])
    for p in payments:
        writer.writerow([p.group.name, p.amount, p.payment_date, p.notes])
    return response