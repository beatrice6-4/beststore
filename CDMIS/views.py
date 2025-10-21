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
    paginate_by = 9  # Show 9 groups per page

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




from django import forms
from django.http import HttpResponse

class FinanceDateForm(forms.Form):
    dates = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Dates"
    )

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

        payments = Payment.objects.select_related('group').order_by('payment_date')
        finance_data = defaultdict(list)
        date_choices = set()
        for payment in payments:
            finance_data[payment.payment_date].append({
                'group': payment.group.name,
                'amount': payment.amount
            })
            date_choices.add(payment.payment_date)

        finance_list = []
        for date, items in finance_data.items():
            date_total = sum(item['amount'] for item in items)
            finance_list.append({
                'date': date,
                'payments': items,
                'date_total': date_total
            })
        finance_list.sort(key=lambda x: x['date'])

        grand_total = payments.aggregate(total=Sum('amount'))['total'] or 0

        # Prepare date choices for the form
        date_choices = sorted(list(date_choices))
        form = FinanceDateForm()
        form.fields['dates'].choices = [(str(d), d.strftime("%b %d, %Y")) for d in date_choices]

        return render(request, self.template_name, {
            'finance_list': finance_list,
            'grand_total': grand_total,
            'form': form,
        })

    def post(self, request, *args, **kwargs):
        # Handle download request
        form = FinanceDateForm(request.POST)
        payments = Payment.objects.select_related('group').order_by('payment_date')
        date_choices = sorted(set(payment.payment_date for payment in payments))
        form.fields['dates'].choices = [(str(d), d.strftime("%b %d, %Y")) for d in date_choices]

        if form.is_valid():
            selected_dates = form.cleaned_data['dates']
            selected_payments = payments.filter(payment_date__in=selected_dates)

            # Prepare CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=finance_summary.csv'
            import csv
            writer = csv.writer(response)
            writer.writerow(['Date', 'Group', 'Amount'])
            total = 0
            for payment in selected_payments:
                writer.writerow([
                    payment.payment_date.strftime("%Y-%m-%d"),
                    payment.group.name,
                    payment.amount
                ])
                total += payment.amount
            writer.writerow([])
            writer.writerow(['', 'Total', total])
            return response

        # If form is not valid, re-render page
        return self.get(request)




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
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from .models import Payment
import os
from django.conf import settings

def download_payments_pdf_by_date(request, payment_date):
    payments = Payment.objects.filter(payment_date=payment_date)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payments_{payment_date}.pdf"'
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
    import os
    from django.conf import settings

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Add GOV logo
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'gov.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, inch, height - 1.5*inch, width=1.2*inch, preserveAspectRatio=True, mask='auto')

    p.setFont("Helvetica-Bold", 16)
    p.drawString(2.5*inch, height - 1*inch, f"Payments for {payment_date}")

    # Table headers
    p.setFont("Helvetica-Bold", 11)
    y = height - 2*inch
    p.drawString(inch, y, "Group")
    p.drawString(2.5*inch, y, "Amount")
    p.drawString(3.5*inch, y, "Date")
    p.drawString(5*inch, y, "Notes")
    y -= 0.3*inch

    # Table rows
    p.setFont("Helvetica", 10)
    for payment in payments:
        p.drawString(inch, y, str(payment.group.name))
        p.drawString(2.5*inch, y, f"Ksh. {payment.amount}")
        p.drawString(3.5*inch, y, str(payment.payment_date))
        p.drawString(5*inch, y, str(payment.notes)[:40])  # Truncate notes for layout
        y -= 0.25*inch
        if y < 1*inch:
            p.showPage()
            y = height - 1*inch

    p.showPage()
    p.save()
    return response







def contact_messages(request):
    # Your logic here (fetch messages if you have a model)
    return render(request, 'CDMIS/contact_messages.html')






from django.shortcuts import render, redirect
from .models import Order  # Adjust import to your actual Order model
from .forms import OrderForm  # Create this form for adding orders
from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cdmis:order_list')
    else:
        form = OrderForm()
    return render(request, 'CDMIS/order_list.html', {'orders': orders, 'form': form})





from django.shortcuts import render, redirect, get_object_or_404
from .models import Order
from .forms import OrderForm

def order_list(request):
    orders = Order.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cdmis:order_list')
    else:
        form = OrderForm()
    return render(request, 'CDMIS/order_list.html', {'orders': orders, 'form': form})

def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('cdmis:order_list')
    else:
        form = OrderForm(instance=order)
    return render(request, 'CDMIS/order_edit.html', {'form': form, 'order': order})

def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('cdmis:order_list')
    return render(request, 'CDMIS/order_delete.html', {'order': order})

from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    return render(request, 'CDMIS/profile.html')

from .models import Group


def group_members(request, pk):
    group = get_object_or_404(Group, id=pk)
    members = group.members.all()  # Assuming related_name='members'
    return render(request, 'CDMIS/group_members.html', {'group': group, 'members': members})

from .models import Member

def member_list(request):
    members = Member.objects.all()
    return render(request, 'CDMIS/member_list.html', {'members': members})

# views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import MemberUploadForm
from .models import Member
import openpyxl
from django.contrib.auth.decorators import user_passes_test

import datetime

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def upload_members(request):
    if request.method == 'POST':
        form = MemberUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            wb = openpyxl.load_workbook(excel_file)
            ws = wb.active
            rows = list(ws.iter_rows(min_row=2, values_only=True))  # skip header

            for row in rows:
                first_name = row[0]
                middle_name = row[1]
                id_no = row[2]
                date_of_birth = row[3]
                gender = row[4]
                email = row[5] if len(row) > 5 else ''
                member_role = row[6] if len(row) > 6 else ''
                disability = row[7] if len(row) > 7 else ''

                # Robust date_of_birth handling
                dob = None
                if isinstance(date_of_birth, datetime.date):
                    dob = date_of_birth
                elif isinstance(date_of_birth, str):
                    try:
                        dob = datetime.date.fromisoformat(date_of_birth)
                    except Exception:
                        dob = None
                elif date_of_birth is None:
                    dob = None

                Member.objects.update_or_create(
                    id_no=id_no,
                    defaults={
                        'first_name': first_name,
                        'middle_name': middle_name,
                        'date_of_birth': dob,
                        'gender': gender,
                        'email': email,
                        'member_role': member_role,
                        'disability': disability,
                    }
                )
            messages.success(request, "Members uploaded successfully!")
            return redirect('cdmis:member_list')
    else:
        form = MemberUploadForm()
    return render(request, 'CDMIS/upload_members.html', {'form': form})



from django.shortcuts import render
from django.db.models import Sum
from .models import Group, Payment, Training

def cdmis_reports(request):
    total_financials = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0

    group_payments = (
        Group.objects
        .annotate(total_paid=Sum('payments__amount'))  # <-- corrected here
        .values('name', 'total_paid')
    )
    below_5000 = [g for g in group_payments if (g['total_paid'] or 0) < 5000]
    above_5000 = [g for g in group_payments if (g['total_paid'] or 0) >= 5000]

    total_trainings = Training.objects.count()
    total_groups = Group.objects.count()

    context = {
        'total_financials': total_financials,
        'below_5000_groups': below_5000,
        'above_5000_groups': above_5000,
        'total_groups': total_groups,
        'total_trainings': total_trainings,
    }
    return render(request, 'CDMIS/reports.html', context)



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django import forms
from .models import Group, Member

# --- Case Management Form ---
class CaseManagementForm(forms.Form):
    CASE_CHOICES = [
        ('change_office_bearers', 'Change of Office Bearers'),
        ('add_member', 'Addition of Group Member'),
        ('exit_member', 'Exit of Group Member'),
        ('correct_member', 'Correction of Member Details'),
    ]
    case_type = forms.ChoiceField(choices=CASE_CHOICES, label="Case Type")
    group = forms.ModelChoiceField(queryset=Group.objects.all(), label="Group")
    member = forms.ModelChoiceField(queryset=Member.objects.all(), required=False, label="Member (if applicable)")
    details = forms.CharField(widget=forms.Textarea, required=False, label="Details / Notes")

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def case_management(request):
    form = CaseManagementForm(request.POST or None)
    message = None

    if request.method == 'POST' and form.is_valid():
        case_type = form.cleaned_data['case_type']
        group = form.cleaned_data['group']
        member = form.cleaned_data.get('member')
        details = form.cleaned_data.get('details')

        if case_type == 'change_office_bearers':
            message = f"Office bearers for group '{group.name}' have been updated."
        elif case_type == 'add_member':
            if member:
                group.members.add(member)  # Add member to group
                group.save()
                member_name = member.first_name
                if hasattr(member, 'middle_name') and member.middle_name:
                    member_name += f" {member.middle_name}"
                message = f"Member '{member_name}' added to group '{group.name}'."
            else:
                message = "Please select a member to add."
        elif case_type == 'exit_member':
            if member:
                group.members.remove(member)
                group.save()
                member_name = member.first_name
                if hasattr(member, 'middle_name') and member.middle_name:
                    member_name += f" {member.middle_name}"
                message = f"Member '{member_name}' exited from group '{group.name}'."
            else:
                message = "Please select a member to exit."
        elif case_type == 'correct_member':
            if member:
                member_name = member.first_name
                if hasattr(member, 'middle_name') and member.middle_name:
                    member_name += f" {member.middle_name}"
                message = f"Details for member '{member_name}' have been corrected."
            else:
                message = "Please select a member to correct."

    return render(request, 'CDMIS/case_management.html', {
        'form': form,
        'message': message,
    })

from django.shortcuts import render, redirect
from .forms import GroupForm

def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cdmis:groups')
    else:
        form = GroupForm()
    return render(request, 'CDMIS/group_form.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from .models import Requirement
from .forms import RequirementForm
import csv

def requirements_list(request):
    requirements = Requirement.objects.all()
    return render(request, 'CDMIS/requirements.html', {'requirements': requirements})

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def create_requirement(request):
    if request.method == 'POST':
        form = RequirementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cdmis:requirements')
    else:
        form = RequirementForm()
    return render(request, 'CDMIS/create_requirement.html', {'form': form})

from django.http import HttpResponse
from .models import Requirement
from docx import Document

def download_requirements_word(request):
    requirements = Requirement.objects.all()
    document = Document()
    document.add_heading('Group Registration Requirements', 0)

    for req in requirements:
        document.add_heading(req.title, level=1)
        document.add_paragraph(req.description)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=group_requirements.docx'
    document.save(response)
    return response


from django.shortcuts import render

def updates(request):
    # You can fetch updates from your model if you have one, or use static data
    updates_list = [
        {"title": "New Training Announced", "date": "2025-10-09", "content": "Join our new training session next week."},
        {"title": "Financial Report Released", "date": "2025-10-08", "content": "The latest financial report is now available."},
    ]
    return render(request, 'CDMIS/updates.html', {'updates': updates_list})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Document
from .forms import DocumentForm

@login_required
def docs(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            form = DocumentForm(request.POST, request.FILES)
            if form.is_valid():
                doc = form.save(commit=False)
                doc.uploaded_by = request.user
                doc.save()
                return redirect('cdmis:docs')
        else:
            form = DocumentForm()
    else:
        form = None
    return render(request, 'CDMIS/docs.html', {'documents': documents, 'form': form})


