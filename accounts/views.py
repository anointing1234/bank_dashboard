from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.html import strip_tags
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout as auth_logout,login as auth_login,authenticate
from django.contrib.auth.decorators import login_required
from django.db.models.signals import post_save
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_protect
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password,check_password
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
import os
from django.conf import settings
import shutil
from requests.exceptions import ConnectionError
import requests 
import uuid
from accounts.form import SignupForm,LoginForm,TransferForm,LoanRequestForm,CardForm,SendresetcodeForm,PasswordResetForm
from .models import PaymentGateway,Deposit, Transaction,Transfer,TransferCode,LoanRequest,ExchangeRate,Exchange,Card,ResetPassword,Beneficiary
import random
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe






def login_view(request):
    form = LoginForm()
    return render(request, 'forms/login.html',{'form':form})  

def signup_view(request):
    form = SignupForm()   
    return render(request, 'forms/signup.html',{'form':form})

def Loan_view(request):
    # Fetch the loan requests for the logged-in user
    user_loans = LoanRequest.objects.filter(user=request.user)
    return render(request, 'loans.html',{'user_loans': user_loans})

def exchange_view(request):
    exchange_rates = ExchangeRate.objects.last() 
    exchange_transactions = Exchange.objects.filter(user=request.user.username).order_by('-id')
    return render(request,'exchanges.html',{
        'exchange_rates': exchange_rates,
        'exchange_transactions': exchange_transactions

        })


def request_loan(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            loan_request = form.save(commit=False)
            loan_request.user = request.user  # Associate the loan request with the logged-in user
            
            # Set the interest rate from the form data
            loan_request.interest_rate = form.cleaned_data.get('interest_rate')
            
            loan_request.save()
            return JsonResponse({'success': "Your loan request has been submitted successfully!"})
        else:
            # Collect error messages
            error_messages = form.errors.as_json()
            return JsonResponse({'error': error_messages}, status=400)  # Return errors with a 400 status code
    else:
        form = LoanRequestForm()

    return render(request, 'loans.html', {'form': form})


def register(request):
    if request.method == 'POST':
        register_form = SignupForm(request.POST)

        if register_form.is_valid():
            user = register_form.save(commit=False)
            
            # Generate a unique username (e.g., first 5 characters of the email + random 4-digit number)
            base_username = user.email.split('@')[0][:5]
            unique_username = f"{base_username}{str(uuid.uuid4().int)[:4]}"
            user.username = unique_username
            
            user.save()  # Save the user with the generated username
            
            return JsonResponse({'success': True, 'message': 'Registration successful!', 'redirect_url': '/Accounts/login'})
        else:
            # Collect all form errors
            error_messages = []
            if register_form.errors:
                for field, errors in register_form.errors.items():
                    for error in errors:
                        error_messages.append(f"{field.capitalize()}: {error}")
            error_message = "\n".join(error_messages)

            return JsonResponse({'success': False, 'message': error_message})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})




def login_Account(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        
        if login_form.is_valid():
            email = login_form.cleaned_data.get('email')
            password = login_form.cleaned_data.get('password')
            dashboard_url = reverse('dashboard')
            # Authenticate the user
            user = authenticate(request, username=email, password=password)
             
            if user is not None:
                auth_login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful!',
                    'redirect_url': dashboard_url
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid email or password. Please try again.'
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Invalid form submission. Please check your details.'
        })
    
    else:
        form = LoginForm()
    
    return render(request, 'forms/login.html', {'form': form})
    


def logout_view(request):
    auth_logout(request)
    form = LoginForm()
    return render(
    request,'forms/login.html',{'form':form})



#   transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
#     deposits = Deposit.objects.filter(user=request.user).order_by('-date')


def deposit_view(request):
    deposits = Deposit.objects.filter(user=request.user).order_by('-date')
    return render(request,'finaces/deposit.html',{'deposits':deposits})
    

def withdrawal_view(request):
    return render(request,'finaces/withdraw.html')

def transfer_view(request):
    # Instantiate the form with the current user
    form = TransferForm(user=request.user)
    
    # Build a dictionary of the user's beneficiaries
    beneficiary_data = {
        beneficiary.id: {
            "full_name": beneficiary.full_name,
            "account_number": beneficiary.account_number,
            "bank_name": beneficiary.bank_name,
            "swift_code": beneficiary.swift_code,
        }
        for beneficiary in Beneficiary.objects.filter(user=request.user)
    }
    
    # Convert the dictionary to JSON for the template
    beneficiary_data_json = json.dumps(beneficiary_data)
    
    # Get transactions of type "transfer" for the logged-in user
    other_transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
    transfers = other_transactions.filter(transaction_type="transfer")
    
    return render(request, 'finaces/transfer.html', {
        'form': form,
        'transfers': transfers,
        'beneficiary_data_json': beneficiary_data_json,
    })



def get_payment_gateway(request):
    network = request.GET.get('network')
    try:
        gateway = PaymentGateway.objects.get(network=network)
        data = {
            "deposit_address": gateway.deposit_address,
            "instructions": gateway.instructions or ""
        }
        return JsonResponse(data)
    except PaymentGateway.DoesNotExist:
        return JsonResponse({"error": "No gateway found"}, status=404)


def create_deposit(request):
    user = request.user
    network = request.POST.get('network')
    amount = request.POST.get('amount')

    # Basic validation
    if not network or not amount:
        return JsonResponse({"error": "Missing required fields."}, status=400)
    
    try:
        # Retrieve the PaymentGateway record for the selected network
        gateway = PaymentGateway.objects.get(network=network)
    except PaymentGateway.DoesNotExist:
        return JsonResponse({"error": "No payment gateway configured for this network."}, status=400)

    try:
        # Generate a unique transaction reference (TNX)
        txn_ref = str(uuid.uuid4()).replace('-', '')[:10].upper()

        # 1) Create Deposit record
        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            network=network,
            TNX=txn_ref,
            status="pending"
        )

        # 2) Create corresponding Transaction record
        Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type="deposit",
            status="pending",  # or "completed" if processed immediately
            description=f"Deposit via {network}",
            reference=txn_ref,
            # Use PaymentGateway details for additional fields
            institution="Payment Gateway",  # Customize if needed
            region="International",  # Fill in if applicable
            from_account=gateway.deposit_address,  # The deposit address for the network
            to_account=user.email  # You could use the user's account number if available
        )

        return JsonResponse({"status": "ok", "message": "Deposit created successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


        


def send_transfer_code(request):
    if request.method == "POST" and request.user.is_authenticated:
        transfer_code = get_random_string(6, allowed_chars="1234567890")  # Generate 6-digit code
        
        # Save the code in the database with expiration time (e.g., 10 minutes)
        TransferCode.objects.create(
            user=request.user,
            transfer_code=transfer_code,
            expires_at=now() + timedelta(minutes=60)  # Set expiration to 10 minutes from now
        )

        # Send email
        send_mail(
                "Your Transfer Code",
                f"Your transfer code is: {transfer_code}",
                settings.DEFAULT_FROM_EMAIL,  # ✅ Use the correct email
                [request.user.email],
                fail_silently=False,
        )

        return JsonResponse({"success": True, "message": "Transfer code sent to your email."})
    
    return JsonResponse({"success": False, "message": "Failed to send transfer code."}, status=400)




def create_transfer(request):
    if request.method == "POST":
        form = TransferForm(request.POST, user=request.user)  # Pass the user here
        print("Received POST data:", request.POST)  # Log the raw POST data
        
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.user = request.user
            currency = form.cleaned_data["currency"]
            amount = form.cleaned_data["amount"]

            # Get the transfer code from the cleaned data and strip whitespace
            transfer_code_input = request.POST.get("transfer_code", "").strip()
            if not transfer_code_input:
                print("Transfer code is missing.")
                return JsonResponse({"success": False, "message": "Transfer code is required."}, status=400)
            print(f"Received transfer code: '{transfer_code_input}'")
        
            account_balance = request.user.account_balance
            print(f"User account balance before transfer: USD={account_balance.available_balance}, GBP={account_balance.gbp}, EUR={account_balance.eur}")

            # Check if the transfer code is valid
            try:
                transfer_code_obj = TransferCode.objects.get(user=request.user, transfer_code=transfer_code_input, used=False)
                print(f"Transfer code found: {transfer_code_obj.transfer_code}")  # Debug print
            except TransferCode.DoesNotExist:
                print("Invalid transfer code.")
                return JsonResponse({"success": False, "message": "Invalid transfer code."}, status=400)

            # Deduct from the correct balance
            if currency == "USD":
                if account_balance.available_balance < amount:
                    print("Insufficient USD balance.")
                    return JsonResponse({"success": False, "message": "Insufficient USD balance."}, status=400)
                account_balance.available_balance -= amount
                account_balance.total_debits  += amount
            elif currency == "GBP":
                if account_balance.gbp < amount:
                    print("Insufficient GBP balance.")
                    return JsonResponse({"success": False, "message": "Insufficient GBP balance."}, status=400)
                account_balance.gbp -= amount
                account_balance.total_debits  += amount
            elif currency == "EUR":
                if account_balance.eur < amount:
                    print("Insufficient EUR balance.")
                    return JsonResponse({"success": False, "message": "Insufficient EUR balance."}, status=400)
                account_balance.eur -= amount
                account_balance.total_debits  += amount
            else:
                print("Invalid currency.")
                return JsonResponse({"success": False, "message": "Invalid currency."}, status=400)

            account_balance.save()
            print(f"User account balance after transfer: USD={account_balance.available_balance}, GBP={account_balance.gbp}, EUR={account_balance.eur}")

            # Generate a unique reference if not already set
            unique_reference = str(uuid.uuid4())[:10]
            transfer.reference = unique_reference
            print(f"Generated unique reference: {unique_reference}")

            # Save the transfer
            try:
                transfer.save()
                print("Transfer saved successfully.")
            except IntegrityError:
                print("Duplicate transfer reference.")
                return JsonResponse({"success": False, "message": "Duplicate transfer reference. Please try again."}, status=400)

            # Create a Transaction record (using bank_account as destination)
            transaction = Transaction(
                user=request.user,
                amount=amount,
                transaction_type='transfer',  # Assuming this is a valid choice
                description=f"Transfer of {amount} {currency} to account {transfer.beneficiary.account_number}",
                reference=unique_reference,
                from_account=request.user.email,  # Adjust as needed
                to_account=transfer.beneficiary.account_number,
                institution="Maybank",  # Adjust as needed
                region=transfer.region,  # Use transfer region
            )
            transaction.save()
            print("Transaction record created successfully.")

            # Mark the transfer code as used
            transfer_code_obj.used = True
            transfer_code_obj.save()
            print("Transfer code marked as used.")

            # Optionally, clear all transfer codes (you might want to reconsider this)
            TransferCode.objects.all().delete()
            print("All transfer codes cleared.")

            # Send email to the user with (a new) transfer code for next transfer if needed
            try:
                send_mail(
                    "Your Transfer Code",
                    f"Your transfer verification code is: {transfer_code_obj.transfer_code}",
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )
                print("Transfer code email sent successfully.")
                return JsonResponse({"success": True, "message": "Transfer successful."})
            except Exception as e:
                print(f"Error sending email: {e}")
                return JsonResponse({"success": False, "message": "Error sending email. Please check your email settings."}, status=500)
        else:
            print("Form is invalid:", form.errors)
            return JsonResponse({"success": False, "message": "Invalid form submission."}, status=400)
    else:
        form = TransferForm(user=request.user)  # Pass the user here as well
    return render(request, "finances/transfer.html", {"form": form})





def update_fullname(request):
    fullname = request.POST.get('fullname')
    if fullname:
        request.user.fullname = fullname
        request.user.save()
        return JsonResponse({'success': 'Full name updated successfully!'})
    return JsonResponse({'error': 'Failed to update full name.'}, status=400)



def swap_currency(request):
    if request.method == "POST":
        data = json.loads(request.body)
        amount = Decimal(data["amount"])
        from_currency = data["from_currency"]
        to_currency = data["to_currency"]
        user_balance = request.user.account_balance

        if from_currency == to_currency:
            return JsonResponse({"success": False, "message": "Cannot swap the same currency!"})

        # Check if the user has enough balance
        if from_currency == "USD" and user_balance.available_balance < amount:
            return JsonResponse({"success": False, "message": "Insufficient USD balance!"})
        if from_currency == "GBP" and user_balance.gbp < amount:
            return JsonResponse({"success": False, "message": "Insufficient GBP balance!"})
        if from_currency == "EUR" and user_balance.eur < amount:
            return JsonResponse({"success": False, "message": "Insufficient EUR balance!"})

        # Get the exchange rate
        exchange_rate = ExchangeRate.objects.last()
        rate = 1
        if from_currency == "EUR" and to_currency == "USD":
            rate = exchange_rate.eur_usd
        elif from_currency == "GBP" and to_currency == "USD":
            rate = exchange_rate.gbp_usd
        elif from_currency == "EUR" and to_currency == "GBP":
            rate = exchange_rate.eur_gbp
        elif from_currency == "USD" and to_currency == "EUR":
            rate = 1 / exchange_rate.eur_usd
        elif from_currency == "USD" and to_currency == "GBP":
            rate = 1 / exchange_rate.gbp_usd
        elif from_currency == "GBP" and to_currency == "EUR":
            rate = 1 / exchange_rate.eur_gbp

        converted_amount = amount * rate

        # Deduct from source balance
        if from_currency == "USD":
            user_balance.available_balance -= amount
        elif from_currency == "GBP":
            user_balance.gbp -= amount
        elif from_currency == "EUR":
            user_balance.eur -= amount

        # Add to destination balance
        if to_currency == "USD":
            user_balance.available_balance += converted_amount
        elif to_currency == "GBP":
            user_balance.gbp += converted_amount
        elif to_currency == "EUR":
            user_balance.eur += converted_amount

        user_balance.save()

        Exchange.objects.create(
            user=request.user.username,  # Using username as the identifier
            amount=amount,  # Corrected to use amount instead of paid/expects
            from_currency=from_currency,
            to_currency=to_currency,
            status='completed',
            date=timezone.now()  # Automatically setting the date
        )

        return JsonResponse({"success": True, "message": f"Swapped {amount} {from_currency} to {converted_amount:.2f} {to_currency}"})

    return JsonResponse({"success": False, "message": "Invalid request"})



def cards_view(request):
    cards = Card.objects.filter(user=request.user)
    return render(request,'cards.html',{'cards': cards})



def add_card(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CardForm(data)

        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return JsonResponse({'status': 'success', 'message': 'Card added successfully!'})
        return JsonResponse({'status': 'error', 'message': 'Invalid card details!'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request!'}, status=400)   


def get_statements(request):
    statement_type = request.GET.get("statement_type")
    if statement_type == "deposit":
        # Adjust the filter to match your deposit transactions (e.g., transaction_type="deposit")
        transactions = Transaction.objects.filter(user=request.user, transaction_type="deposit").order_by("-transaction_date")
    elif statement_type == "transfer":
        transactions = Transaction.objects.filter(user=request.user, transaction_type="transfer").order_by("-transaction_date")
    else:
        return JsonResponse({"success": False, "message": "Invalid statement type."}, status=400)

    data = []
    for tx in transactions:
        data.append({
            "reference": tx.reference,
            "date": tx.transaction_date.strftime("%Y-%m-%d %H:%M"),  # Format as desired
            "amount": str(tx.amount),
            "status": tx.status,
        })

    return JsonResponse({"success": True, "statements": data})







def send_reset_code_view(request):
    if request.method == 'POST':
        form = SendresetcodeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Check if the email is registered
            User = get_user_model()  # Get the custom user model
            if not User.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'This email address is not registered.'})

            # Generate a reset code
            reset_code = get_random_string(length=7)  # Generate a random string as the reset code
            
            # Store the reset code in the database
            ResetPassword.objects.update_or_create(
                email=email,
                defaults={'reset_code': reset_code}
            )
            
            # Send the email
            send_mail(
                'Password Reset Code',
                f'Your password reset code is: {reset_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True, 'message': 'A password reset code has been sent to your email.'})
        else:
            return JsonResponse({'success': False, 'message': form.errors['email'][0]})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})





def reset_password_view(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)  # Use a different variable name
        if form.is_valid():
            email = form.cleaned_data['email']
            reset_code = form.cleaned_data['reset_code']
            new_password = form.cleaned_data['new_password']

            # Check if the reset code is valid for the given email
            try:
                reset_entry =  ResetPassword.objects.get(email=email, reset_code=reset_code)
            except PasswordResetCode.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Invalid reset code or email.'})

            # Update the user's password
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)  # Set the new password
                user.save()

                # Optionally, delete the reset code after use
                reset_entry.delete()

                messages.success(request, "Your password has been reset successfully.")
                return JsonResponse({'success': True, 'message': 'Your password has been reset successfully.'})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User  not found.'})

    else:
        form = PasswordResetForm()  # This is now correctly instantiated

    return render(request,'forms/reset_pass.html', {'form': form})



def send_pass(request):
    form = SendresetcodeForm()
    return render(request,'forms/send_reset_code.html',{'form':form})






@login_required
def add_beneficiary(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        account_number = request.POST.get('account_number')
        bank_name = request.POST.get('bank_name')
        swift_code = request.POST.get('swift_code', '')
        
        # Validate required fields
        if not (full_name and account_number and bank_name):
            return JsonResponse({'success': False, 'message': 'Please fill in all required fields.'}, status=400)
        
        # Create the beneficiary
        beneficiary = Beneficiary.objects.create(
            user=request.user,
            full_name=full_name,
            account_number=account_number,
            bank_name=bank_name,
            swift_code=swift_code
        )
        return JsonResponse({'success': True, 'message': 'Beneficiary added successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)

