import random
import string
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from PIL import Image
import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.html import format_html
from decimal import Decimal
import uuid
import json
import locale



# Define choices for account type
ACCOUNT_TYPE_CHOICES = (
    ('savings', 'Savings'),
    ('current', 'Current'),
    ('fixed', 'Fixed Deposit'),
)

class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and returns a regular user"""
        if not email:
            raise ValueError("User must have an email address")
        
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])  # Default username from email
        extra_fields.setdefault('account_type', 'savings')

        first_name = extra_fields.pop('first_name', '')
        last_name = extra_fields.pop('last_name', '')
        phone_number = extra_fields.pop('phone_number', '')

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Creates and returns a superuser"""
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email=email, password=password, **extra_fields)

class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="Email", max_length=100, unique=True)
    username = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    account_type = models.CharField(
        max_length=20,
        choices=ACCOUNT_TYPE_CHOICES,
        default='savings',
        help_text="Type of bank account (e.g., Savings, Current, Fixed Deposit)"
    )
    date_joined = models.DateTimeField(verbose_name="Date Joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="Last Login", auto_now=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Django’s built-in staff flag
    is_superuser = models.BooleanField(default=False)  # Django’s built-in superuser flag

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Superusers have all permissions"""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Grant access to Django admin panel"""
        return self.is_superuser or self.is_staff




class AccountBalance(models.Model):
    # Use the string reference to avoid circular imports
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='account_balance'
    )
    
    # Account details
    available_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    loan_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_credits = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_debits = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    gbp = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Pounds: £1.23 / $
    eur = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Euro: €1.03 / $

    def __str__(self):
        return f"Account Balance for {self.account.email}"


CARD_TYPE_CHOICES = (
    ('credit', 'Credit'),
    ('debit', 'Debit'),
    ('prepaid', 'Prepaid'),
)

VENDOR_CHOICES = (
    ('visa', 'Visa'),
    ('mastercard', 'MasterCard'),
    ('amex', 'American Express'),
    ('discover', 'Discover'),
)

STATUS_CHOICES = (
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('blocked', 'Blocked'),
)

class Card(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cards'
    )
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='debit')
    vendor = models.CharField(max_length=20, choices=VENDOR_CHOICES, default='visa')
    # The 'account' field represents the card number.
    # It is not auto-generated. It is optional and can be filled later by the user.
    account = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # New field for card password. Ensure you store this securely (hashed) in production.
    card_password = models.CharField(
        max_length=128, 
        null=True, 
        blank=True, 
        help_text="Password or PIN for the card"
    )

    def __str__(self):
        return f"{self.vendor.upper()} {self.card_type.capitalize()} Card for {self.user.email}"





STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('declined', 'Declined'),
)

class LoanRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='loan_requests',
        help_text="User who requested the loan"
    )
    date = models.DateTimeField(auto_now_add=True, help_text="Date when the request was made")
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        help_text="Amount requested"
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
        help_text="Currency of the loan (e.g., USD, EUR, GBP)"
    )
    loan_type = models.CharField(
        max_length=50,
        help_text="Type of loan (e.g., personal, home, auto)",
        default="personal",
    )
    reason = models.TextField(help_text="Reason for the loan request")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the loan request"
    )
    # Additional fields for robust overseas loan processing:
    term_months = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Loan term in months"
    )
    interest_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Annual interest rate (%)"
    )
    collateral = models.TextField(
        null=True, 
        blank=True, 
        help_text="Collateral details (if any)"
    )
    approval_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date and time when the loan was approved"
    )
    disbursement_date = models.DateTimeField(
        null=True, 
        blank=True, 
        help_text="Date and time when the funds were disbursed"
    )
    repayment_start_date = models.DateField(
        null=True, 
        blank=True, 
        help_text="Date when repayment starts"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_loans",
        help_text="Administrator who approved the loan"
    )
    status_detail = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Additional details about the loan status"
    )

    def __str__(self):
        return f"Loan Request by {self.user.email} on {self.date:%Y-%m-%d}"

    def clean(self):
        """
        Add any custom validation here, e.g., ensuring that if the loan is approved,
        then certain fields (like approval_date) must be set.
        """
        # Example: If status is approved, approval_date should not be None.
        if self.status == 'approved' and self.approval_date is None:
            from django.core.exceptions import ValidationError
            raise ValidationError("Approved loans must have an approval date.")






STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('cancelled', 'Cancelled'),
)

class Exchange(models.Model):
    # Free-standing user identifier (email or username)
    user = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="User identifier (e.g., email or username)"
    )
    # The exchanged amount (converted amount)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Exchanged amount",
        default=0.00
    )
    # The source currency code (e.g., USD)
    from_currency = models.CharField(
        max_length=100,
        help_text="USD"
    )
    # The destination currency code (e.g., EUR)
    to_currency = models.CharField(
        max_length=100,
        help_text="EUR"
    )
    # The status of the exchange
    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the exchange"
    )
    # Date and time of the exchange
    date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of the exchange"
    )

    def __str__(self):
        return f"Exchange for {self.user or 'Unknown User'}: {self.amount} from {self.from_currency} to {self.to_currency} - {self.status}"



class ResetPassword(models.Model):
    email = models.EmailField(unique=True)
    reset_code = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email   


class TransferCode(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transfer_codes"
    )
    transfer_code = models.CharField(max_length=10, unique=True, help_text="Code for transfers")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text="Code expiration time")
    used = models.BooleanField(default=False, help_text="Has the code been used?")

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)  # Set to 1 hour from now
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if the transfer code is valid (not expired or used)."""
        return not self.used and self.expires_at > timezone.now()

    def __str__(self):
        return f"Transfer Code for {self.user.email} (Valid: {self.is_valid()})"


# Define choices for transaction type and status
TRANSACTION_TYPE_CHOICES = (
    ('deposit', 'Deposit'),
    ('withdrawal', 'Withdrawal'),
    ('transfer', 'Transfer'),
    ('payment', 'Payment'),
)

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
)

class Transaction(models.Model):
    # The user who made the transaction
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='transactions'
    )
    # Automatically set the transaction date when the record is created
    transaction_date = models.DateTimeField(auto_now_add=True)
    # The amount involved in the transaction
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    # The type of transaction (deposit, withdrawal, transfer, payment, etc.)
    transaction_type = models.CharField(
        max_length=20, 
        choices=TRANSACTION_TYPE_CHOICES
    )
    # An optional description or memo for the transaction
    description = models.TextField(blank=True, null=True)
    # The current status of the transaction
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    # Unique reference for the transaction
    reference = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="Optional unique reference for the transaction"
    )
    # New fields
    institution = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Institution involved in the transaction"
    )
    region = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Region where the transaction occurred"
    )
    from_account = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Debit account or source of funds"
    )
    to_account = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Credit account or destination of funds"
    )

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of {self.amount} by {self.user} on {self.transaction_date:%Y-%m-%d}"




# Deposit status choices
DEPOSIT_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
)

class Deposit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='deposits'
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    TNX = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Transaction reference or ID"
    )
    network = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Network used for the deposit (e.g., Ethereum, Bitcoin)"
    )
    rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.00,
        help_text="Exchange rate at the time of deposit"
    )
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=DEPOSIT_STATUS_CHOICES,
        default='pending'
    )

    def __str__(self):
        return f"Deposit of {self.amount} by {self.user.email} on {self.date:%Y-%m-%d}"




# Define available networks (you can expand these as needed)
NETWORK_CHOICES = (
    ('Ethereum', 'Ethereum'),
    ('Bitcoin', 'Bitcoin'),
    ('USDT', 'USDT'),
)

class PaymentGateway(models.Model):
    network = models.CharField(
        max_length=50,
        choices=NETWORK_CHOICES,
        unique=True,
        help_text="The network for which this deposit address applies."
    )
    deposit_address = models.CharField(
        max_length=255,
        help_text="The deposit address for the given network."
    )
    qr_code = models.ImageField(
        upload_to='payment_gateways/',
        blank=True,
        null=True,
        help_text="Optional QR code for the deposit address."
    )
    instructions = models.TextField(
        blank=True,
        null=True,
        help_text="Additional instructions for deposits on this network."
    )

    def __str__(self):
        return f"{self.network} Gateway"

    class Meta:
        verbose_name = "Payment Gateway"
        verbose_name_plural = "Payment Gateways"





class Transfer(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transfers'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)  # Allows large amounts
    currency = models.CharField(max_length=10, default="USD")  # Default currency
    reference = models.CharField(max_length=50, unique=True)  # Unique transfer reference
    date = models.DateTimeField(auto_now_add=True)  # Auto-filled timestamp
    reason = models.TextField(blank=True, null=True)  # Optional reason
    region = models.CharField(max_length=50, default="local")  # Default to local transfers
    charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Transfer fees
    bank_country = models.CharField(max_length=50, blank=True, null=True)  # Can be None for local transfers
    bank_name = models.CharField(max_length=100)  # Bank name
    bank_account = models.CharField(max_length=50)  # Recipient bank account number
    bank_holder = models.CharField(max_length=100)  # Name of the recipient
    identifier = models.CharField(max_length=100, blank=True, null=True)  # Optional identifier
    identifier_code = models.CharField(max_length=100, blank=True, null=True)  # Optional identifier code
    sender_name = models.CharField(max_length=100)  # Name of the sender
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  # Transfer status

    def __str__(self):
        return f"Transfer {self.reference} - {self.status}"






class ExchangeRate(models.Model):
    eur_usd = models.DecimalField(max_digits=10, decimal_places=4, help_text="Exchange rate from EUR to USD")
    gbp_usd = models.DecimalField(max_digits=10, decimal_places=4, help_text="Exchange rate from GBP to USD")
    eur_gbp = models.DecimalField(max_digits=10, decimal_places=4, help_text="Exchange rate from EUR to GBP")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp of the last update")

    def __str__(self):
        return f"EUR/USD: {self.eur_usd}, GBP/USD: {self.gbp_usd}, EUR/GBP: {self.eur_gbp}"
