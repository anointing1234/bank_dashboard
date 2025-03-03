from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.contrib.auth import login,authenticate
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
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
from email.mime.image import MIMEImage
from django.conf import settings
import shutil
from requests.exceptions import ConnectionError
import requests 
import uuid
from accounts.form import SignupForm,LoginForm,TransferForm,LoanRequestForm,CardForm,SendresetcodeForm,PasswordResetForm,ProfileEditForm 
from .models import PaymentGateway,Deposit, Transaction,Transfer,TransferCode,LoanRequest,ExchangeRate,Exchange,Card,ResetPassword,Beneficiary,AccountBalance
import random
from django.utils.crypto import get_random_string
from django.utils.timezone import now, timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
import logging



logger = logging.getLogger(__name__)





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
            
            # Prepare email content
            current_year = timezone.now().year
            email_subject = 'Welcome to Maybank'
            email_body = render_to_string('emails/registration_email.html', {
                'user': user,
                'current_year': current_year,
            })

            # Create the email
            msg = EmailMultiAlternatives(
                email_subject,
                '',  # Plain text message (optional)
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
            msg.mixed_subtype = 'related'  # Allow inline images

            # Attach the HTML content
            msg.attach_alternative(email_body, "text/html")

            # Attach the logo as an inline image
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')  # Adjust the path as necessary
            with open(logo_path, 'rb') as f:  # Open the logo file in binary mode
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<logo.png>')  # Set the content ID
                img.add_header('Content-Disposition', 'inline', filename='logo.png')  # Set as inline
                msg.attach(img)  # Attach the image to the email

            # Send the email
            msg.send(fail_silently=False)

            return JsonResponse({'success': True, 'message': 'A welcome email has been sent with your account id.', 'redirect_url': '/Accounts/login'})
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


def emails(request):
    return render(request,'emails/registration_email.html')




def login_Account(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        
        if login_form.is_valid():
            account_id = login_form.cleaned_data.get('account_id')  # Get the account ID or email
            password = login_form.cleaned_data.get('password')
            dashboard_url = reverse('dashboard')
            
            # Authenticate the user using the custom backend
            user = authenticate(request, username=account_id, password=password)
             
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
                    'message': 'Invalid Account ID or password. Please try again.'
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
            "routing_transit_number":beneficiary.routing_transit_number,
            "bank_address":beneficiary.bank_address
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





def validate_pin(request):
   
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "User not authenticated."})
    
    pin = request.POST.get("pin")
    if not pin:
        return JsonResponse({"success": False, "message": "PIN not provided."})
    
    # Assumes that the Account model (or custom User model) has a field 'transaction_pin'.
    if request.user.pin == pin:
        return JsonResponse({"success": True, "message": "PIN validated successfully."})
    else:
        return JsonResponse({"success": False, "message": "Incorrect transaction PIN."})




def create_deposit(request):
    user = request.user
    network = request.POST.get('network')
    amount = request.POST.get('amount')
    account_type = request.POST.get('account')

    logger.debug(f":User  {user}, Network: {network}, Amount: {amount}, Account Type: {account_type}")

    # Basic validation
    if not network or not amount or not account_type:
        return JsonResponse({"error": "Missing required fields."}, status=400)

    try:
        # Convert amount to Decimal
        amount = Decimal(amount)

        # Generate a unique transaction reference (TNX)
        txn_ref = str(uuid.uuid4()).replace('-', '')[:10].upper()

        # 1) Create Deposit record
        deposit = Deposit.objects.create(
            user=user,
            amount=amount,
            network=network,
            TNX=txn_ref,
            status="completed",
            account=account_type,
        )

        # 2) Create corresponding Transaction record
        Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type="deposit",
            status="pending",
            description=f"Deposit via {network}",
            reference=txn_ref,
            institution="Payment Gateway",
            region="International",
            from_account="N/A",
            to_account=user.email
        )

        # 3) Update the appropriate balance based on account type
        account_balance = get_object_or_404(AccountBalance, account=user)

        if account_type == 'Savings_Account':
            account_balance.available_balance += amount
            account_balance.total_credits += amount
        elif account_type == 'Checking_Account':
            account_balance.checking_balance += amount
            account_balance.total_credits += amount

        account_balance.save()

        return JsonResponse({"status": "ok", "message": "Deposit created successfully."})
    except InvalidOperation:
        logger.error("Invalid amount provided.")
        return JsonResponse({"error": "Invalid amount."}, status=400)
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


def send_transfer_code(request):
    if request.method == "POST" and request.user.is_authenticated:
        # Check if there are any unused codes (status=False)
        existing_code = TransferCode.objects.filter(user=request.user,  used=False).first()
        
        if existing_code:
            return JsonResponse({"success": True})
        
        # Generate new codes
        tac_code = get_random_string(6, allowed_chars="1234567890")
        tax_code = get_random_string(6, allowed_chars="1234567890")
        imf_code = get_random_string(6, allowed_chars="1234567890")
        
        # Save the new codes in the database with an expiration time
        TransferCode.objects.create(
            user=request.user,
            tac_code=tac_code,
            tax_code=tax_code,
            imf_code=imf_code,
            expires_at=now() + timedelta(minutes=120),
            used=False  # Mark as unused
        )
        
        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False}, status=400)



def create_transfer(request):
    if request.method == "POST":
        form = TransferForm(request.POST, user=request.user)  # Pass the user here
        print("Received POST data:", request.POST)  # Log the raw POST data
        
        if form.is_valid():
            transfer = form.save(commit=False)
            transfer.user = request.user
            currency = form.cleaned_data["from_account"]
            amount = form.cleaned_data["amount"]

            # Get the codes from the POST data (strip whitespace)
            tac_code_input = request.POST.get("tac_code", "").strip()
            tax_code_input = request.POST.get("tax_code", "").strip()
            imf_code_input = request.POST.get("imf_code", "").strip()

            # Check if all codes are provided
            if not tac_code_input or not tax_code_input or not imf_code_input:
                print("One or more codes are missing.")
                return JsonResponse({"success": False, "message": "All codes are required."}, status=400)

            print(f"Received codes: TAC='{tac_code_input}', Tax='{tax_code_input}', IMF='{imf_code_input}'")

            account_balance = request.user.account_balance
            print(f"User account balance before transfer: USD={account_balance.available_balance}, GBP={account_balance.gbp}, EUR={account_balance.eur}")

            # Verify TAC code
            try:
                tac_code_obj = TransferCode.objects.get(user=request.user, tac_code=tac_code_input, used=False)
                print(f"TAC code found: {tac_code_obj.tac_code}")
            except TransferCode.DoesNotExist:
                print("Invalid TAC code.")
                return JsonResponse({"success": False, "message": "Invalid TAC code."}, status=400)

            # Verify Tax code
            try:
                tax_code_obj = TransferCode.objects.get(user=request.user, tax_code=tax_code_input, used=False)
                print(f"Tax code found: {tax_code_obj.tax_code}")
            except TransferCode.DoesNotExist:
                print("Invalid Tax code.")
                return JsonResponse({"success": False, "message": "Invalid Tax code."}, status=400)

            # Verify IMF code
            try:
                imf_code_obj = TransferCode.objects.get(user=request.user, imf_code=imf_code_input, used=False)
                print(f"IMF code found: {imf_code_obj.imf_code}")
            except TransferCode.DoesNotExist:
                print("Invalid IMF code.")
                return JsonResponse({"success": False, "message": "Invalid IMF code."}, status=400)

            if currency == "savings":
                if account_balance.available_balance < amount:
                    print("Insufficient Savings balance.")
                    return JsonResponse({"success": False, "message": "Insufficient Savings balance."}, status=400)
                account_balance.available_balance -= amount
                account_balance.total_debits += amount
                remaining_balance = account_balance.available_balance
            elif currency == "checking":
                if account_balance.checking_balance < amount:
                    print("Insufficient Checking balance.")
                    return JsonResponse({"success": False, "message": "Insufficient Checking balance."}, status=400)
                account_balance.checking_balance -= amount
                account_balance.total_debits += amount
                remaining_balance = account_balance.checking_balance
            elif currency == "gbp":
                if account_balance.gbp < amount:
                    print("Insufficient GBP balance.")
                    return JsonResponse({"success": False, "message": "Insufficient GBP balance."}, status=400)
                account_balance.gbp -= amount
                account_balance.total_debits += amount
                remaining_balance = account_balance.gbp
            elif currency == "eur":
                if account_balance.eur < amount:
                    print("Insufficient EUR balance.")
                    return JsonResponse({"success": False, "message": "Insufficient EUR balance."}, status=400)
                account_balance.eur -= amount
                account_balance.total_debits += amount
                remaining_balance = account_balance.eur
            else:
                print("Invalid balance.")
                return JsonResponse({"success": False, "message": "Invalid balance."}, status=400)

            account_balance.save()
            print(f"User account balance after transfer: USD={account_balance.available_balance}, GBP={account_balance.gbp}, EUR={account_balance.eur}")

            # Generate a unique transaction reference
            unique_reference = str(uuid.uuid4())[:10]
            transfer.reference = unique_reference
            print(f"Generated unique reference: {unique_reference}")

            try:
                transfer.save()
                print("Transfer saved successfully.")
            except IntegrityError:
                print("Duplicate transfer reference.")
                return JsonResponse({"success": False, "message": "Duplicate transfer reference. Please try again."}, status=400)

            # Create a Transaction record
            transaction = Transaction(
                user=request.user,
                amount=amount,
                transaction_type='transfer',
                description=f"Transfer of {amount} {currency} to account {transfer.beneficiary.account_number}",
                reference=unique_reference,
                from_account=request.user.email,
                to_account=transfer.beneficiary.account_number,
                institution="Maybank",
                region=transfer.region,
            )
            transaction.save()
            print("Transaction record created successfully.")

            # Mark the transfer codes as used
            tac_code_obj.used = True
            tax_code_obj.used = True
            imf_code_obj.used = True
            tac_code_obj.save()
            tax_code_obj.save()
            imf_code_obj.save()
            print("Transfer codes marked as used.")
                        # ------------------------------------------------------------------
            # Send Debit Notification Email using EmailMultiAlternatives
            # ------------------------------------------------------------------
            debit_context = {
                "user": request.user,
                "amount": amount,
                "sender_account_type": transfer.from_account,
                "sender_account_number": request.user.account_number,
                "sender_name": f"{request.user.first_name} {request.user.last_name}",
                "transaction_reference": unique_reference,
                "transaction_date": transaction.transaction_date,
                "available_balance":remaining_balance,
            }
            email_subject = "Debit Notification"
            email_body = render_to_string("emails/debit_notification.html", debit_context)
            msg = EmailMultiAlternatives(
                email_subject,
                "",  # Plain text version (optional)
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
            )
            msg.mixed_subtype = "related"  # Allow inline images

            # Attach the HTML alternative
            msg.attach_alternative(email_body, "text/html")

            # Attach the logo as an inline image (using the same procedure as in registration)
            logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')  # Adjust path if needed
            with open(logo_path, 'rb') as f:
                img = MIMEImage(f.read())
                img.add_header('Content-ID', '<logo.png>')
                img.add_header('Content-Disposition', 'inline', filename='logo.png')
                msg.attach(img)

            try:
                msg.send(fail_silently=False)
                print("Debit notification email sent successfully.")
            except Exception as e:
                print(f"Error sending debit notification email: {e}")
                return JsonResponse({"success": False, "message": "Error sending debit notification email. Please check your email settings."}, status=500)

            # ------------------------------------------------------------------
            # Return the Redirect URL in JSON
            # ------------------------------------------------------------------
            receipt_url = reverse("transaction_receipt", args=[unique_reference])
            return JsonResponse({
                "success": True,
                "message": "Transfer successful.",
                "redirect_url": receipt_url
            })
        else:
            print("Form is invalid:", form.errors)
            return JsonResponse({"success": False, "message": "Invalid form submission."}, status=400)
    else:
        form = TransferForm(user=request.user)
    return render(request, "finances/transfer.html", {"form": form})





def validate_code(request):
    if request.method == "POST":
        code = request.POST.get("code")
        code_type = request.POST.get("code_type")

        if not code or not code_type:
            return JsonResponse({"success": False, "message": "Code and code type are required."}, status=400)

        try:
            if code_type == "tac_code":
                code_obj = TransferCode.objects.get(user=request.user, tac_code=code, used=False)
            elif code_type == "tax_code":
                code_obj = TransferCode.objects.get(user=request.user, tax_code=code, used=False)
            elif code_type == "imf_code":
                code_obj = TransferCode.objects.get(user=request.user, imf_code=code, used=False)
            else:
                return JsonResponse({"success": False, "message": "Invalid code type."}, status=400)

            return JsonResponse({"success": True, "message": f"{code_type.replace('_', ' ').title()} is valid."})

        except TransferCode.DoesNotExist:
            return JsonResponse({"success": False, "message": f"Invalid {code_type.replace('_', ' ')}."}, status=400)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

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






def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # Save the updated user profile
            return JsonResponse({'success': True})
        else:
            # Collect error messages
            error_messages = form.errors.as_json()
            return JsonResponse({'success': False, 'error': error_messages})
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form})



def transaction_receipt(request, reference):
    # Retrieve the transaction and transfer objects based on the reference and current user.
    transaction = get_object_or_404(Transaction, reference=reference, user=request.user)
    transfer = get_object_or_404(Transfer, reference=reference, user=request.user)
    
    context = {
        "sender_name": f"{request.user.first_name} {request.user.last_name}",
        "sender_account_number": request.user.account_number,
        "sender_account_type": request.user.account_type,
        "receiver_name": transfer.beneficiary.full_name,
        "receiver_account_number": transfer.beneficiary.account_number,
        "receiver_bank": transfer.beneficiary.bank_name,
        "receiver_bank_address": transfer.beneficiary.bank_address,
        "transaction_reference": reference,
        "transaction_date": transaction.transaction_date,
        "region": transfer.region,
        "amount": transaction.amount,
        "currency": transfer.balance,
        "available_balance": request.user.account_balance.available_balance,
    }
    return render(request, 'emails/transaction_receipt.html', context)



def deposit_statements(request):
    # Fetch deposit transactions for the logged-in user
    transactions = Transaction.objects.filter(user=request.user, transaction_type='deposit').order_by('-transaction_date')
    
    context = {
        'transactions': transactions,
    }
    return render(request, 'finaces/deposit_statements.html', context)

def transfer_statements(request):
    # Fetch transfer transactions for the logged-in user
    transactions = Transaction.objects.filter(user=request.user, transaction_type='transfer').order_by('-transaction_date')
    
    context = {
        'transactions': transactions,
    }
    return render(request, 'finaces/transfer_statements.html', context)