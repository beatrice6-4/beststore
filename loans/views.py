from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
import json

from .models import LoanApplication, LoanDocument, LoanVerification
from .forms import (
    LoanApplicationForm, LoanDocumentFormSet, LoanVerificationForm,
    LoanDisbursementForm, LoanFilterForm
)


def is_admin(user):
    """Check if user is staff/admin"""
    return user.is_staff


@login_required
def loan_application_list(request):
    """Display user's loan applications"""
    applications = LoanApplication.objects.filter(user=request.user)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status:
        applications = applications.filter(status=status)
    
    # Search
    search = request.GET.get('search', '')
    if search:
        applications = applications.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(national_id__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(applications, 10)
    page = request.GET.get('page', 1)
    applications = paginator.get_page(page)
    
    context = {
        'applications': applications,
        'title': 'My Loan Applications',
        'status_filter': status,
        'search': search,
    }
    return render(request, 'loans/application_list.html', context)


@login_required
def loan_application_create(request):
    """Create new loan application"""
    # Check if user already has pending application
    pending = LoanApplication.objects.filter(
        user=request.user,
        status='pending'
    ).first()
    
    if pending:
        messages.warning(request, 'You already have a pending loan application.')
        return redirect('loans:application_detail', pk=pending.pk)
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.email = request.user.email
            application.save()
            
            messages.success(
                request,
                'Loan application submitted successfully! Your application is pending verification.'
            )
            return redirect('loans:application_detail', pk=application.pk)
    else:
        form = LoanApplicationForm()
    
    context = {
        'form': form,
        'title': 'Apply for Loan',
        'is_create': True,
    }
    return render(request, 'loans/application_form.html', context)


@login_required
def loan_application_detail(request, pk):
    """View loan application details"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    # Check permission
    if application.user != request.user and not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this application.')
        return redirect('loans:application_list')
    
    documents = application.documents.all()
    verifications = application.verifications.all()
    
    context = {
        'application': application,
        'documents': documents,
        'verifications': verifications,
        'title': f'Application - {application.get_full_name()}',
    }
    return render(request, 'loans/application_detail.html', context)


@login_required
def loan_application_edit(request, pk):
    """Edit loan application (only pending)"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    # Check permission
    if application.user != request.user:
        messages.error(request, 'You do not have permission to edit this application.')
        return redirect('loans:application_list')
    
    # Can only edit pending applications
    if application.status != 'pending':
        messages.error(request, 'You can only edit pending applications.')
        return redirect('loans:application_detail', pk=pk)
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, request.FILES, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Application updated successfully.')
            return redirect('loans:application_detail', pk=pk)
    else:
        form = LoanApplicationForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
        'title': 'Edit Application',
    }
    return render(request, 'loans/application_form.html', context)


@login_required
def loan_documents_upload(request, pk):
    """Upload supporting documents"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    # Check permission
    if application.user != request.user:
        messages.error(request, 'You do not have permission.')
        return redirect('loans:application_list')
    
    if request.method == 'POST':
        formset = LoanDocumentFormSet(request.POST, request.FILES, instance=application)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Documents uploaded successfully.')
            return redirect('loans:application_detail', pk=pk)
    else:
        formset = LoanDocumentFormSet(instance=application)
    
    context = {
        'formset': formset,
        'application': application,
        'title': 'Upload Documents',
    }
    return render(request, 'loans/documents_upload.html', context)


# ==================== ADMIN VIEWS ====================

@login_required
@user_passes_test(is_admin)
def loan_admin_dashboard(request):
    """Admin dashboard with loan statistics"""
    total_applications = LoanApplication.objects.count()
    pending = LoanApplication.objects.filter(status='pending').count()
    verified = LoanApplication.objects.filter(status='verified').count()
    disbursed = LoanApplication.objects.filter(status='disbursed').count()
    rejected = LoanApplication.objects.filter(status='rejected').count()
    
    # Recent applications
    recent = LoanApplication.objects.all()[:10]
    
    context = {
        'total_applications': total_applications,
        'pending': pending,
        'verified': verified,
        'disbursed': disbursed,
        'rejected': rejected,
        'recent': recent,
        'title': 'Loan Management Dashboard',
    }
    return render(request, 'loans/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def loan_admin_list(request):
    """Admin view all loan applications"""
    applications = LoanApplication.objects.all()
    
    # Filter
    form = LoanFilterForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('status'):
            applications = applications.filter(status=form.cleaned_data['status'])
        
        if form.cleaned_data.get('search'):
            search = form.cleaned_data['search']
            applications = applications.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(national_id__icontains=search) |
                Q(phone_number__icontains=search)
            )
        
        if form.cleaned_data.get('date_from'):
            applications = applications.filter(
                created_at__gte=form.cleaned_data['date_from']
            )
        
        if form.cleaned_data.get('date_to'):
            applications = applications.filter(
                created_at__lte=form.cleaned_data['date_to']
            )
    
    # Ordering
    sort_by = request.GET.get('sort', '-created_at')
    applications = applications.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(applications, 20)
    page = request.GET.get('page', 1)
    applications = paginator.get_page(page)
    
    context = {
        'applications': applications,
        'form': form,
        'title': 'Loan Applications',
    }
    return render(request, 'loans/admin/application_list.html', context)


@login_required
@user_passes_test(is_admin)
def loan_admin_verify(request, pk):
    """Admin verify/reject loan application"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    if request.method == 'POST':
        form = LoanVerificationForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            notes = form.cleaned_data.get('verification_notes', '')
            
            application.verified_by = request.user
            application.verified_at = timezone.now()
            application.verification_notes = notes
            
            if status == 'verified':
                application.status = 'verified'
                messages.success(request, 'Application verified successfully.')
            else:
                application.status = 'rejected'
                application.rejection_reason = form.cleaned_data.get('rejection_reason', '')
                application.rejected_at = timezone.now()
                messages.success(request, 'Application rejected.')
            
            application.save()
            return redirect('loans:admin_list')
    else:
        form = LoanVerificationForm()
    
    context = {
        'application': application,
        'form': form,
        'title': 'Verify Application',
    }
    return render(request, 'loans/admin/verify_application.html', context)


@login_required
@user_passes_test(is_admin)
def loan_admin_disburse(request, pk):
    """Admin process loan disbursement"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    # Check if verified
    if application.status != 'verified':
        messages.error(request, 'Application must be verified before disbursement.')
        return redirect('loans:admin_list')
    
    if request.method == 'POST':
        form = LoanDisbursementForm(request.POST)
        if form.is_valid():
            application.bank_name = form.cleaned_data['bank_name']
            application.account_number = form.cleaned_data['account_number']
            application.status = 'disbursed'
            application.disbursed_at = timezone.now()
            application.save()
            
            messages.success(
                request,
                f'Loan of KES {application.loan_amount} disbursed successfully.'
            )
            return redirect('loans:admin_list')
    else:
        form = LoanDisbursementForm()
    
    context = {
        'application': application,
        'form': form,
        'title': 'Process Disbursement',
    }
    return render(request, 'loans/admin/disburse.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def loan_geolocation_api(request, pk):
    """API endpoint to get geolocation data"""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    data = {
        'latitude': application.latitude,
        'longitude': application.longitude,
        'address': application.address,
        'city': application.city,
        'county': application.county,
    }
    return JsonResponse(data)
