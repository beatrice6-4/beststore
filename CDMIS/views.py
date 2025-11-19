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
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Q
from datetime import datetime, timedelta
from .models import Payment, Group
import json


class FinanceView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Finance view for displaying financial summary and payment records.
    Only accessible to staff members and group leaders.
    Displays payments grouped by date with daily totals and grand total.
    """
    template_name = 'CDMIS/finance.html'
    login_url = 'login'

    def test_func(self):
        """
        Test if user is staff or group leader.
        Returns True if user has permission to view finances.
        """
        return self.request.user.is_staff or self.request.user.groups.filter(name='Group Leaders').exists()

    def handle_no_permission(self):
        """
        Handle when user doesn't have permission.
        """
        from django.shortcuts import redirect
        from django.contrib import messages
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    def get_finance_data(self, start_date=None, end_date=None, selected_dates=None):
        """
        Get financial data from the database.
        
        Args:
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering
            selected_dates: List of specific dates to filter by
        
        Returns:
            List of dicts with date, payments, and date_total
        """
        # Base queryset
        payments = Payment.objects.select_related('group', 'user').order_by('-date', 'group__name')

        # Filter by user if not staff
        if not self.request.user.is_staff:
            payments = payments.filter(
                Q(group__leaders=self.request.user) | 
                Q(user=self.request.user)
            )

        # Date filtering
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                payments = payments.filter(date__gte=start)
            except ValueError:
                pass

        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                payments = payments.filter(date__lte=end)
            except ValueError:
                pass

        # Specific dates filtering
        if selected_dates:
            date_list = []
            for date_str in selected_dates:
                try:
                    date_list.append(datetime.strptime(date_str, '%Y-%m-%d').date())
                except ValueError:
                    pass
            if date_list:
                payments = payments.filter(date__in=date_list)

        # Group by date
        finance_list = []
        current_date = None
        current_payments = []
        date_total = 0

        for payment in payments:
            if current_date != payment.date:
                # Save previous date group
                if current_date is not None:
                    finance_list.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'date_display': current_date.strftime('%A, %B %d, %Y'),
                        'payments': current_payments,
                        'date_total': f"{date_total:,.2f}",
                        'date_total_raw': date_total,
                    })
                
                # Start new date group
                current_date = payment.date
                current_payments = []
                date_total = 0

            # Add payment to current group
            current_payments.append({
                'id': payment.id,
                'group': payment.group.name if payment.group else 'Individual',
                'group_id': payment.group.id if payment.group else None,
                'amount': f"{float(payment.amount):,.2f}",
                'amount_raw': float(payment.amount),
                'description': payment.description or 'Payment',
                'payment_method': payment.payment_method or 'Cash',
                'reference': payment.reference or 'N/A',
                'user': payment.user.get_full_name() or payment.user.username,
            })
            date_total += float(payment.amount)

        # Add last date group
        if current_date is not None:
            finance_list.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'date_display': current_date.strftime('%A, %B %d, %Y'),
                'payments': current_payments,
                'date_total': f"{date_total:,.2f}",
                'date_total_raw': date_total,
            })

        return finance_list

    def calculate_totals(self, finance_list):
        """
        Calculate grand totals from finance list.
        
        Args:
            finance_list: List of finance data by date
        
        Returns:
            Dict with total_payments, grand_total, date_range
        """
        total_payments = 0
        grand_total = 0.0
        first_date = None
        last_date = None

        for date_group in finance_list:
            for payment in date_group['payments']:
                total_payments += 1
                grand_total += payment['amount_raw']
            
            if first_date is None:
                first_date = date_group['date']
            last_date = date_group['date']

        return {
            'total_payments': total_payments,
            'grand_total': f"{grand_total:,.2f}",
            'grand_total_raw': grand_total,
            'first_date': first_date,
            'last_date': last_date,
            'date_range': f"{first_date} to {last_date}" if first_date and last_date else "N/A",
        }

    def get_date_options(self):
        """
        Get all unique dates available for filtering.
        
        Returns:
            List of dates with payment counts
        """
        payments = Payment.objects.values('date').annotate(
            count=Sum('id'),
            total=Sum('amount')
        ).order_by('-date')

        # Filter by user if not staff
        if not self.request.user.is_staff:
            payment_ids = Payment.objects.filter(
                Q(group__leaders=self.request.user) | 
                Q(user=self.request.user)
            ).values_list('id', flat=True)
            payments = payments.filter(id__in=payment_ids)

        date_options = []
        for payment in payments:
            date_options.append({
                'date': payment['date'].strftime('%Y-%m-%d'),
                'display': payment['date'].strftime('%a, %b %d, %Y'),
                'count': payment['count'],
                'total': f"{float(payment['total']):,.2f}",
            })

        return date_options

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests.
        Display financial summary with all data.
        """
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        selected_dates = request.GET.getlist('dates')

        # Get finance data
        finance_list = self.get_finance_data(start_date, end_date, selected_dates)
        
        # Calculate totals
        totals = self.calculate_totals(finance_list)

        # Get date options for filter
        date_options = self.get_date_options()

        context = {
            'finance_list': finance_list,
            'date_options': date_options,
            'grand_total': totals['grand_total'],
            'total_payments': totals['total_payments'],
            'date_range': totals['date_range'],
            'page_title': 'Financial Summary',
            'breadcrumb': 'Finance',
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for filtered data.
        Returns JSON response with filtered finance data.
        """
        try:
            data = json.loads(request.body)
            selected_dates = data.get('dates', [])
            start_date = data.get('start_date')
            end_date = data.get('end_date')

            # Get finance data
            finance_list = self.get_finance_data(start_date, end_date, selected_dates)
            
            # Calculate totals
            totals = self.calculate_totals(finance_list)

            return JsonResponse({
                'success': True,
                'finance_list': finance_list,
                'totals': totals,
                'message': f'Loaded {totals["total_payments"]} payments'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class FinanceExportView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Export finance data as CSV or PDF.
    Only accessible to staff members.
    """
    login_url = 'login'

    def test_func(self):
        """Only staff can export data."""
        return self.request.user.is_staff

    def get(self, request, *args, **kwargs):
        """
        Export finance data.
        Query params:
            - format: 'csv' or 'pdf' (default: csv)
            - dates: comma-separated list of dates
        """
        export_format = request.GET.get('format', 'csv')
        dates_str = request.GET.get('dates', '')
        
        # Parse dates
        selected_dates = [d.strip() for d in dates_str.split(',') if d.strip()]

        # Get payments
        payments = Payment.objects.select_related('group', 'user').order_by('-date')
        
        if selected_dates:
            date_list = []
            for date_str in selected_dates:
                try:
                    date_list.append(datetime.strptime(date_str, '%Y-%m-%d').date())
                except ValueError:
                    pass
            if date_list:
                payments = payments.filter(date__in=date_list)

        if export_format == 'csv':
            return self._export_csv(payments)
        elif export_format == 'pdf':
            return self._export_pdf(payments)
        else:
            return JsonResponse({'error': 'Invalid format'}, status=400)

    def _export_csv(self, payments):
        """Export payments as CSV."""
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="finance-export-{datetime.now().strftime("%Y%m%d")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Group', 'Amount', 'Method', 'Reference', 'User'])

        for payment in payments:
            writer.writerow([
                payment.date.strftime('%Y-%m-%d'),
                payment.group.name if payment.group else 'Individual',
                float(payment.amount),
                payment.payment_method or 'Cash',
                payment.reference or '',
                payment.user.get_full_name() or payment.user.username,
            ])

        # Add totals row
        total = sum(float(p.amount) for p in payments)
        writer.writerow(['', 'TOTAL', total, '', '', ''])

        return response

    def _export_pdf(self, payments):
        """Export payments as PDF."""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from django.http import HttpResponse
            from datetime import datetime

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="finance-export-{datetime.now().strftime("%Y%m%d")}.pdf"'

            # Create PDF
            doc = SimpleDocTemplate(response, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()

            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f3a5f'),
                spaceAfter=30,
                alignment=1
            )
            elements.append(Paragraph('Financial Summary Report', title_style))
            elements.append(Spacer(1, 0.3*inch))

            # Table data
            data = [['Date', 'Group', 'Amount', 'Method', 'Reference', 'User']]
            total = 0

            for payment in payments:
                data.append([
                    payment.date.strftime('%Y-%m-%d'),
                    payment.group.name if payment.group else 'Individual',
                    f"Ksh {float(payment.amount):,.2f}",
                    payment.payment_method or 'Cash',
                    payment.reference or '',
                    payment.user.get_full_name() or payment.user.username,
                ])
                total += float(payment.amount)

            # Add total row
            data.append(['', '', f"Ksh {total:,.2f}", '', '', 'TOTAL'])

            # Create table
            table = Table(data, colWidths=[1.2*inch, 1.2*inch, 1*inch, 0.8*inch, 1*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f3a5f')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#eafbe7')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))

            elements.append(table)
            doc.build(elements)
            return response

        except ImportError:
            return JsonResponse({
                'error': 'PDF export requires reportlab. Install with: pip install reportlab'
            }, status=500)


class FinanceStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    API endpoint for finance statistics.
    Returns JSON data for dashboard widgets.
    """
    login_url = 'login'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name='Group Leaders').exists()

    def get(self, request, *args, **kwargs):
        """
        Get finance statistics.
        Query params:
            - period: 'today', 'week', 'month', 'year' (default: month)
        """
        period = request.GET.get('period', 'month')
        today = datetime.now().date()

        # Determine date range
        if period == 'today':
            start_date = today
        elif period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:  # month
            start_date = today - timedelta(days=30)

        # Get payments
        payments = Payment.objects.filter(date__gte=start_date).select_related('group')

        if not request.user.is_staff:
            payments = payments.filter(
                Q(group__leaders=request.user) | 
                Q(user=request.user)
            )

        # Calculate stats
        stats = {
            'total_amount': float(payments.aggregate(Sum('amount'))['amount__sum'] or 0),
            'total_payments': payments.count(),
            'average_payment': float(payments.aggregate(Sum('amount'))['amount__sum'] or 0) / max(payments.count(), 1),
            'period': period,
        }

        # By payment method
        by_method = payments.values('payment_method').annotate(
            total=Sum('amount'),
            count=Sum('id')
        )
        stats['by_method'] = list(by_method)

        # By group
        by_group = payments.values('group__name').annotate(
            total=Sum('amount'),
            count=Sum('id')
        ).order_by('-total')
        stats['by_group'] = list(by_group)

        return JsonResponse(stats)


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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Update, Booking
from django.contrib import messages

@login_required
def updates(request):
    updates_list = Update.objects.all().order_by('-date')  # Fetch updates from the database

    if request.method == 'POST':
        update_id = request.POST.get('update_id')
        update = get_object_or_404(Update, id=update_id)

        # Check if the user has already booked this update
        if Booking.objects.filter(user=request.user, update=update).exists():
            messages.error(request, "You have already booked this update.")
        else:
            Booking.objects.create(user=request.user, update=update)
            messages.success(request, "You have successfully booked this update.")

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



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from decimal import Decimal
from .models import FinancialAccount, Withdrawal

BANK_CHOICES = [
    ('', 'Select Bank'),
    ('KCB', 'KCB Bank'),
    ('Equity', 'Equity Bank'),
    ('Cooperative', 'Cooperative Bank'),
    ('Absa', 'Absa Bank'),
    ('Stanbic', 'Stanbic Bank'),
    ('NCBA', 'NCBA Bank'),
    ('Family', 'Family Bank'),
    ('I&M', 'I&M Bank'),
    ('DTB', 'Diamond Trust Bank'),
    ('Standard Chartered', 'Standard Chartered Bank'),
    # ...add more as needed...
]

@login_required
def withdraw_funds(request):
    # Ensure the FinancialAccount exists for the user
    account, created = FinancialAccount.objects.get_or_create(
        user=request.user,
        defaults={'balance': Decimal('6000.00')}
    )

    if request.method == 'POST':
        amount = request.POST.get('amount')
        withdrawal_method = request.POST.get('withdrawal_method')
        phone_number = request.POST.get('phone_number')
        bank_name = request.POST.get('bank_name')
        bank_branch = request.POST.get('bank_branch')
        account_number = request.POST.get('account_number')
        notes = request.POST.get('notes')

        try:
            amount = Decimal(amount)
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect('cdmis:withdraw_funds')

        # Validation
        if amount > account.balance:
            messages.error(request, "Insufficient balance.")
        elif amount <= 0:
            messages.error(request, "Withdrawal amount must be greater than zero.")
        elif not withdrawal_method:
            messages.error(request, "Please select a withdrawal method.")
        elif withdrawal_method in ['mpesa', 'cash_pickup'] and not phone_number:
            messages.error(request, "Phone number is required for this method.")
        elif withdrawal_method == 'bank_transfer' and (not bank_name or not bank_branch or not account_number):
            messages.error(request, "Bank name, branch, and account number are required for bank transfer.")
        else:
            # Deduct the amount and create a withdrawal request
            account.balance -= amount
            account.save()

            withdrawal = Withdrawal.objects.create(
                user=request.user,
                amount=amount,
                withdrawal_method=withdrawal_method,
                phone_number=phone_number if withdrawal_method in ['mpesa', 'cash_pickup'] else None,
                bank_name=bank_name if withdrawal_method == 'bank_transfer' else None,
                bank_branch=bank_branch if withdrawal_method == 'bank_transfer' else None,
                account_number=account_number if withdrawal_method == 'bank_transfer' else None,
                notes=notes,
                status='Pending'
            )

            # Send pending notification email
            send_mail(
                subject='Withdrawal Request Pending',
                message=f'Dear {request.user.first_name},\n\nYour withdrawal request of Ksh {withdrawal.amount} is pending and will be processed soon.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )

            messages.success(request, f"Withdrawal request for {amount} has been submitted and is pending.")
            return redirect('cdmis:withdrawal_list')

    return render(request, 'CDMIS/withdraw_funds.html', {
        'account': account,
        'bank_choices': BANK_CHOICES
    })



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FinancialAccount, Withdrawal
from decimal import Decimal

@login_required
def withdraw_funds(request):
    # Ensure the FinancialAccount exists for the user
    account, created = FinancialAccount.objects.get_or_create(
        user=request.user,
        defaults={'balance': Decimal('6000.00')}  # Default balance is 6,000
    )

    if request.method == 'POST':
        amount = request.POST.get('amount')
        phone_number = request.POST.get('phone_number')

        try:
            # Convert the amount to Decimal
            amount = Decimal(amount)
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            return redirect('cdmis:withdraw_funds')

        # Check if the user has sufficient balance
        if amount > account.balance:
            messages.error(request, "Insufficient balance.")
        elif amount <= 0:
            messages.error(request, "Withdrawal amount must be greater than zero.")
        elif not phone_number:
            messages.error(request, "Phone number is required.")
        else:
            # Deduct the amount and create a withdrawal request
            account.balance -= amount
            account.save()

            Withdrawal.objects.create(user=request.user, amount=amount, phone_number=phone_number, status='Pending')
            messages.success(request, f"Withdrawal request for {amount} has been submitted.")

            # Redirect to the withdrawal list page
            return redirect('cdmis:withdrawal_list')

    return render(request, 'CDMIS/withdraw_funds.html', {'account': account})



from django.views.generic import ListView
from .models import Withdrawal

class WithdrawalListView(ListView):
    model = Withdrawal
    template_name = 'CDMIS/withdrawal_list.html'
    context_object_name = 'withdrawals'

    def get_queryset(self):
        # Show only withdrawals for the logged-in user
        return Withdrawal.objects.filter(user=self.request.user).order_by('-requested_at')





from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import FinancialAccount
from django.contrib import messages
from django import forms

# Form for editing the balance
class EditBalanceForm(forms.ModelForm):
    class Meta:
        model = FinancialAccount
        fields = ['balance']

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def edit_balance(request, pk):
    account = get_object_or_404(FinancialAccount, pk=pk)
    if request.method == 'POST':
        form = EditBalanceForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, f"Balance for {account.user.username} has been updated.")
            return redirect('cdmis:financial_accounts')  # Redirect to a list of financial accounts
    else:
        form = EditBalanceForm(instance=account)
    return render(request, 'CDMIS/edit_balance.html', {'form': form, 'account': account})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def financial_accounts(request):
    accounts = FinancialAccount.objects.all()
    return render(request, 'CDMIS/financial_accounts.html', {'accounts': accounts})


from django.views.generic import DetailView
from .models import Withdrawal

class WithdrawalDetailView(DetailView):
    model = Withdrawal
    template_name = 'CDMIS/withdrawal_detail.html'
    context_object_name = 'withdrawal'