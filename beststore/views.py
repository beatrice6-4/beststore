from django.shortcuts import render
from store.models import Product
from django.contrib.auth.decorators import login_required

def dashboard(request):
    products = Product.objects.all().filter(is_available=True)  # Fetch all available products rom the database


    context = {'products': products}

    return render(request, 'dashboard.html', context)






