from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

def home(request):
    """
    Display CDMIS home page with community development information.
    Shows:
    - Total registered groups
    - Total community members
    - Recent activities and trainings
    - Payment statistics
    - Group information and services
    """
    
    from CDMIS.models import Group, Member, Activity, Training, Service, Payment
    
    # ========================= FETCH CDMIS STATISTICS =========================
    # Total Groups
    total_groups = Group.objects.count()
    groups = Group.objects.all()
    
    # Total Members
    total_members = Member.objects.count()
    
    # Total Payments
    total_payments = Payment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0.0
    
    # Get recent activities (last 10)
    recent_activities = Activity.objects.all().order_by('-activity_date')[:10]
    
    # Get recent trainings (last 10)
    recent_trainings = Training.objects.all().order_by('-training_date')[:10]
    
    # Get all services
    all_services = Service.objects.all().order_by('-service_date')[:10]
    
    # Get recent payments (last 10)
    recent_payments = Payment.objects.all().order_by('-payment_date')[:10]
    
    # ========================= GROUP STATISTICS =========================
    group_stats = []
    for group in groups[:5]:  # Top 5 groups
        group_members = Member.objects.filter(group=group).count()
        group_payments = Payment.objects.filter(group=group).aggregate(
            total=Sum('amount')
        )['total'] or 0.0
        group_activities = Activity.objects.filter(group=group).count()
        
        group_stats.append({
            'group': group,
            'members': group_members,
            'total_paid': group_payments,
            'activities': group_activities,
        })
    
    # ========================= CONTEXT DATA =========================
    context = {
        'page_title': 'CDMIS Home - Community Development Management System',
        'total_groups': total_groups,
        'total_members': total_members,
        'total_payments': total_payments,
        'groups': groups,
        'group_stats': group_stats,
        'recent_activities': recent_activities,
        'recent_trainings': recent_trainings,
        'all_services': all_services,
        'recent_payments': recent_payments,
        'is_authenticated': request.user.is_authenticated,
    }
    
    return render(request, 'home_cdmis.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
def mpesa_transaction_result(request):
    """
    Handle M-Pesa transaction callback.
    This endpoint receives transaction results from M-Pesa API.
    """
    return HttpResponse("OK", status=200)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from store.models import Product
from django.db.models import Sum, Count, Q
from datetime import timedelta, datetime
import requests
import json
import logging
import base64
import os
from django.conf import settings

logger = logging.getLogger(__name__)

# ========================= M-PESA LIVE CONFIGURATION =========================
# Online Buy Goods Transaction
MPESA_CONFIG = {
    'CONSUMER_KEY': os.getenv('MPESA_CONSUMER_KEY', 'kfy4wKPlLpC4AGlZRphJl1VgpzAVc1fNVs4w2l3vNVb1GuqM'),
    'CONSUMER_SECRET': os.getenv('MPESA_CONSUMER_SECRET', '4TgAMbmpG5wbH4mqFpIYZ6tOCGFWGnJjMBvFE7Z4DobFfcJjmvDjLnsWcoIm9FLf'),
    'BUSINESS_SHORTCODE': '3581517',  # Business short code for Buy Goods Online
    'TILL_NUMBER': '6391014',  # Till/PartyB number (where money goes)
    'PASSKEY': os.getenv('MPESA_PASSKEY', '46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933'),
    'ENVIRONMENT': 'production',
    'BASE_URL': 'https://api.safaricom.co.ke',
}


# ========================= M-PESA CLIENT CLASS =========================

class MpesaClient:
    """
    Production M-Pesa API Client for STK Push - Buy Goods Online
    """
    
    def __init__(self):
        # FIX: Use proper dictionary keys with bracket notation
        self.consumer_key = MPESA_CONFIG['kfy4wKPlLpC4AGlZRphJl1VgpzAVc1fNVs4w2l3vNVb1GuqM']
        self.consumer_secret = MPESA_CONFIG['4TgAMbmpG5wbH4mqFpIYZ6tOCGFWGnJjMBvFE7Z4DobFfcJjmvDjLnsWcoIm9FLf']
        self.business_shortcode = MPESA_CONFIG['3581517']
        self.till_number = MPESA_CONFIG['6391014']
        self.passkey = MPESA_CONFIG['46c4b4ea9885ebebe4054aa05ba24ebede63a956de7286c28135be035bdec933']
        self.base_url = MPESA_CONFIG['https://api.safaricom.co.ke']
        self.timeout = 30
    
    def get_access_token(self):
        """
        Get M-Pesa OAuth2 access token for production
        """
        try:
            url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
            
            logger.info('Fetching M-Pesa access token...')
            
            response = requests.get(
                url,
                auth=(self.consumer_key, self.consumer_secret),
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token = response.json().get('access_token')
                logger.info('Access token retrieved successfully')
                return token
            else:
                error_msg = f'Status: {response.status_code}, Response: {response.text}'
                logger.error(f'Failed to get access token: {error_msg}')
                return None
        
        except requests.exceptions.Timeout:
            logger.error('Access token request timeout')
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f'Error getting access token: {str(e)}')
            return None
        except Exception as e:
            logger.error(f'Unexpected error in get_access_token: {str(e)}')
            return None
    
    def stk_push(self, phone_number, amount, account_reference, callback_url):
        """
        Initiate STK Push for Online Buy Goods transaction
        
        Args:
            phone_number: Customer phone number in format 254712345678
            amount: Amount to charge in KES (integer)
            account_reference: Unique transaction reference
            callback_url: URL to receive payment callback
        
        Returns:
            dict with success status and CheckoutRequestID
        """
        try:
            # Get access token
            access_token = self.get_access_token()
            
            if not access_token:
                logger.error('Failed to get access token for STK Push')
                return {
                    'success': False,
                    'error': 'Authentication failed. Please try again.',
                    'error_code': 'AUTH_FAILED'
                }
            
            # Generate timestamp and password
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password_string = f'{self.business_shortcode}{self.passkey}{timestamp}'
            password = base64.b64encode(password_string.encode()).decode()
            
            logger.info(f'STK Push: Amount={amount}, Phone={phone_number}, Ref={account_reference}')
            
            # Prepare STK Push payload for Buy Goods Online
            payload = {
                'BusinessShortCode': self.business_shortcode,
                'Password': password,
                'Timestamp': timestamp,
                'TransactionType': 'CustomerBuyGoodsOnline',
                'Amount': int(amount),
                'PartyA': phone_number,
                'PartyB': self.till_number,
                'PhoneNumber': phone_number,
                'CallBackURL': callback_url,
                'AccountReference': str(account_reference),
                'TransactionDesc': 'BESTSTORE Account Recharge',
            }
            
            # Send STK Push request
            url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            }
            
            logger.info(f'Sending STK Push to {url}')
            logger.info(f'Payload: BusinessShortCode={self.business_shortcode}, PartyB={self.till_number}')
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('ResponseCode') == '0':
                    logger.info(f"STK Push successful: {result.get('CheckoutRequestID')}")
                    return {
                        'success': True,
                        'checkout_request_id': result.get('CheckoutRequestID'),
                        'response_code': result.get('ResponseCode'),
                        'message': result.get('ResponseDescription', 'Payment prompt sent'),
                    }
                else:
                    error_msg = result.get('ResponseDescription', 'Unknown error')
                    logger.warning(f'STK Push returned non-zero code: {error_msg}')
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_code': result.get('ResponseCode')
                    }
            else:
                error_msg = response.text
                logger.error(f'STK Push HTTP error {response.status_code}: {error_msg}')
                return {
                    'success': False,
                    'error': 'Payment service error. Please try again.',
                    'error_code': f'HTTP_{response.status_code}'
                }
        
        except requests.exceptions.Timeout:
            logger.error('STK Push request timeout')
            return {
                'success': False,
                'error': 'Request timeout. Please try again.',
                'error_code': 'TIMEOUT'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f'STK Push request error: {str(e)}')
            return {
                'success': False,
                'error': f'Connection error: {str(e)}',
                'error_code': 'CONNECTION_ERROR'
            }
        except Exception as e:
            logger.error(f'Unexpected error in STK Push: {str(e)}')
            return {
                'success': False,
                'error': 'An unexpected error occurred',
                'error_code': 'UNKNOWN_ERROR'
            }


# ========================= HOME VIEW =========================

def home(request):
    """
    Display home page with products, user statistics, and account information.
    Shows:
    - All available products
    - User order history and statistics (if logged in)
    - Account balance and spending information (if logged in)
    - Featured/trending products
    """
    
    # ========================= FETCH PRODUCTS =========================
    products = Product.objects.filter(
        is_available=True
    ).select_related('category').order_by('-created_at')
    
    featured_products = products[:8]
    
    # ========================= USER AUTHENTICATION CHECK =========================
    user_stats = {
        'is_authenticated': request.user.is_authenticated,
        'total_orders': 0,
        'completed_orders': 0,
        'total_spent': 0.0,
        'pending_orders': 0,
        'pending_amount': 0.0,
        'account_balance': 0.0,
        'recent_orders': [],
    }
    
    # If user is logged in, fetch user-specific data
    if request.user.is_authenticated:
        from orders.models import Order
        from accounts.models import Account
        
        user = request.user
        
        try:
            account = Account.objects.get(id=user.id)
            user_stats['account_balance'] = float(getattr(account, 'account_balance', 0.0) or 0)
        except Account.DoesNotExist:
            user_stats['account_balance'] = 0.0
        except Exception as e:
            logger.error(f"Error fetching account: {str(e)}")
            user_stats['account_balance'] = 0.0
        
        try:
            all_orders = Order.objects.filter(user=user).select_related('user')
            
            user_stats['total_orders'] = all_orders.count()
            
            completed_orders = all_orders.filter(
                status__in=['completed', 'delivered', 'confirmed']
            )
            user_stats['completed_orders'] = completed_orders.count()
            
            spent_data = completed_orders.aggregate(total=Sum('total_amount'))
            user_stats['total_spent'] = float(spent_data['total'] or 0)
            
            pending_orders = all_orders.filter(
                status__in=['pending', 'processing', 'shipped']
            )
            user_stats['pending_orders'] = pending_orders.count()
            
            pending_data = pending_orders.aggregate(total=Sum('total_amount'))
            user_stats['pending_amount'] = float(pending_data['total'] or 0)
            
            user_stats['recent_orders'] = all_orders.order_by('-created_at')[:5]
        
        except Exception as e:
            logger.error(f"Error fetching user statistics: {str(e)}")
            user_stats['recent_orders'] = []
    
    context = {
        'products': products,
        'featured_products': featured_products,
        'total_products': products.count(),
        'user_stats': user_stats,
        'page_title': 'Home - BESTSTORE',
    }
    
    return render(request, 'home.html', context)


# ========================= RECHARGE VIEWS =========================

@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def recharge(request):
    """
    Handle user account recharge with M-Pesa STK Push (PRODUCTION)
    Online Buy Goods Transaction - Business ShortCode: 3581517, Till: 6391014
    
    GET: Display recharge form
    POST: Initiate M-Pesa payment
    """
    
    if request.method == 'GET':
        context = {
            'page_title': 'Recharge Account',
            'breadcrumb': 'Recharge Account',
            'till_number': MPESA_CONFIG['TILL_NUMBER'],
            'business_shortcode': MPESA_CONFIG['BUSINESS_SHORTCODE'],
        }
        return render(request, 'accounts/recharge.html', context)
    
    # POST request - Initiate M-Pesa payment
    if request.method == 'POST':
        try:
            user = request.user
            amount = request.POST.get('amount', '').strip()
            phone = request.POST.get('phone', '').strip()
            
            # ========================= VALIDATION =========================
            
            if not amount:
                messages.error(request, 'Please enter an amount.')
                return redirect('recharge')
            
            # Validate amount
            try:
                amount_float = float(amount)
                if amount_float < 100:
                    messages.error(request, 'Minimum recharge amount is KES 100.')
                    return redirect('recharge')
                if amount_float > 150000:
                    messages.error(request, 'Maximum recharge amount is KES 150,000.')
                    return redirect('recharge')
            except ValueError:
                messages.error(request, 'Please enter a valid amount.')
                return redirect('recharge')
            
            # Validate phone
            if not phone:
                messages.error(request, 'Please enter your phone number.')
                return redirect('recharge')
            
            # Format phone number
            phone = phone.replace(' ', '').replace('-', '').replace('+', '')
            
            if phone.startswith('0'):
                phone = '254' + phone[1:]
            elif not phone.startswith('254'):
                phone = '254' + phone
            
            # Validate phone format
            if not phone.startswith('254') or len(phone) != 12 or not phone.isdigit():
                messages.error(request, 'Please enter a valid Kenyan phone number (e.g., 0712345678).')
                return redirect('recharge')
            
            # ========================= CREATE TRANSACTION =========================
            
            from orders.models import Transaction
            
            transaction_ref = f'RECHARGE_{user.id}_{timezone.now().strftime("%Y%m%d%H%M%S")}'
            
            try:
                transaction = Transaction.objects.create(
                    user=user,
                    amount=amount_float,
                    phone_number=phone,
                    transaction_ref=transaction_ref,
                    status='initiated',
                    transaction_type='recharge'
                )
                
                logger.info(f'Transaction created: {transaction_ref} for user {user.id}')
            
            except Exception as e:
                logger.error(f'Error creating transaction: {str(e)}', exc_info=True)
                messages.error(request, f'Failed to create transaction. Error: {str(e)}')
                return redirect('recharge')
            
            # ========================= INITIATE M-PESA STK PUSH =========================
            
            mpesa_client = MpesaClient()
            callback_url = request.build_absolute_uri('/mpesa/callback/')
            
            logger.info(f'Initiating STK Push: Amount={amount_float}, Phone={phone}')
            logger.info(f'Using Business ShortCode: {MPESA_CONFIG["BUSINESS_SHORTCODE"]}, Till: {MPESA_CONFIG["TILL_NUMBER"]}')
            
            result = mpesa_client.stk_push(
                phone_number=phone,
                amount=int(amount_float),
                account_reference=transaction_ref,
                callback_url=callback_url
            )
            
            if result['success']:
                # Update transaction with checkout request ID
                transaction.checkout_request_id = result.get('checkout_request_id')
                transaction.status = 'pending'
                transaction.save()
                
                logger.info(f'STK Push successful: {result.get("checkout_request_id")}')
                
                messages.success(
                    request,
                    f'🔔 Payment prompt sent to {phone}.\n\n'
                    f'Please enter your M-Pesa PIN to complete the payment of KES {amount_float:,.2f}'
                )
                
                return redirect('recharge_pending', transaction_id=transaction.id)
            
            else:
                # Payment initiation failed
                transaction.status = 'failed'
                transaction.error_message = result.get('error')
                transaction.save()
                
                error_msg = result.get('error', 'Failed to initiate payment')
                logger.error(f'STK Push failed: {error_msg}')
                
                messages.error(
                    request,
                    f'❌ Payment failed: {error_msg}\n\nPlease check your details and try again.'
                )
                
                return redirect('recharge')
        
        except Exception as e:
            logger.error(f'Unexpected error in recharge: {str(e)}', exc_info=True)
            messages.error(request, f'An unexpected error occurred: {str(e)}')
            return redirect('recharge')


@login_required(login_url='login')
def recharge_pending(request, transaction_id):
    """
    Display pending payment status page
    """
    try:
        from orders.models import Transaction
        
        transaction = Transaction.objects.get(
            id=transaction_id,
            user=request.user
        )
        
        context = {
            'page_title': 'Payment Pending',
            'transaction': transaction,
            'breadcrumb': 'Payment Status',
        }
        
        return render(request, 'accounts/recharge_pending.html', context)
    
    except Transaction.DoesNotExist:
        messages.error(request, 'Transaction not found.')
        return redirect('recharge')
    except Exception as e:
        logger.error(f'Error in recharge_pending: {str(e)}')
        messages.error(request, 'An error occurred.')
        return redirect('recharge')


@login_required(login_url='login')
def check_payment_status(request, transaction_id):
    """
    AJAX endpoint to check payment status
    """
    try:
        from orders.models import Transaction
        
        transaction = Transaction.objects.get(
            id=transaction_id,
            user=request.user
        )
        
        return JsonResponse({
            'status': transaction.status,
            'amount': float(transaction.amount),
            'created_at': transaction.created_at.isoformat(),
        })
    
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        logger.error(f'Error checking payment status: {str(e)}')
        return JsonResponse({'error': 'An error occurred'}, status=500)


# ========================= M-PESA CALLBACK =========================

@csrf_exempt
@require_POST
def mpesa_callback(request):
    """
    Handle M-Pesa STK Push callback (PRODUCTION)
    Receives payment status from M-Pesa for Buy Goods Online transaction
    """
    try:
        callback_data = json.loads(request.body)
        
        logger.info(f'M-Pesa Callback received: {json.dumps(callback_data, indent=2)}')
        
        # Extract callback data
        body = callback_data.get('Body', {})
        stk_callback = body.get('stkCallback', {})
        
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        
        logger.info(f'Callback Data: CheckoutID={checkout_request_id}, ResultCode={result_code}')
        
        # Find transaction
        from orders.models import Transaction
        from accounts.models import Account
        
        try:
            transaction = Transaction.objects.get(
                checkout_request_id=checkout_request_id
            )
            
            if result_code == 0:
                # ========================= PAYMENT SUCCESSFUL =========================
                
                logger.info(f'Payment successful: {checkout_request_id}')
                
                transaction.status = 'completed'
                transaction.result_code = result_code
                transaction.result_desc = result_desc
                transaction.save()
                
                # Update user account balance
                try:
                    account = Account.objects.get(id=transaction.user.id)
                    account.account_balance = (account.account_balance or 0) + transaction.amount
                    account.save()
                    
                    logger.info(
                        f'Account balance updated for {transaction.user.email}: '
                        f'New balance = {account.account_balance}'
                    )
                
                except Account.DoesNotExist:
                    logger.error(f'Account not found for user {transaction.user.id}')
                
            else:
                # ========================= PAYMENT FAILED =========================
                
                logger.warning(f'Payment failed: {result_desc}')
                
                transaction.status = 'failed'
                transaction.result_code = result_code
                transaction.result_desc = result_desc
                transaction.save()
        
        except Transaction.DoesNotExist:
            logger.error(f'Transaction not found for CheckoutID: {checkout_request_id}')
        
        # Return success to M-Pesa
        return JsonResponse({'status': 'success'})
    
    except json.JSONDecodeError:
        logger.error('Invalid JSON in M-Pesa callback')
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f'Error processing M-Pesa callback: {str(e)}', exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
def mpesa_transaction_result(request):
    """
    Alternative M-Pesa callback endpoint
    """
    return HttpResponse("OK", status=200)