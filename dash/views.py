from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.html import strip_tags
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_protect
import json
from django.contrib.auth.hashers import make_password,check_password
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
import os
from django.conf import settings
import shutil
from requests.exceptions import ConnectionError
import requests 
from django.contrib.auth.decorators import login_required
from accounts.models import Transaction



@login_required(login_url='login')
def home_view(request):
   other_transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')  # Fetch transactions for logged-in user
   transfer_transactions = other_transactions.filter(transaction_type="transfer")
   return render(request, 'index.html',{
   "transfer_transactions": transfer_transactions,
   "other_transactions": other_transactions
   })

@login_required(login_url='login')
def profile_view(request):
    return render(request, 'profile.html')




    
