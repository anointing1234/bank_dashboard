from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
import base64
from django.core.files import File
from io import BytesIO
from PIL import Image
import os
from django.utils import timezone
from django.contrib import messages
from django.contrib.staticfiles.storage import staticfiles_storage
import json
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django import forms
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Account, AccountBalance, Card, LoanRequest, 
    Exchange, ResetPassword, TransferCode, Transaction,Deposit,PaymentGateway,Transfer,LoanRequest,
    ExchangeRate
)
from django.db import transaction
User = get_user_model()  # Get the custom user model


class AccountAdmin(BaseUserAdmin):
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'account_type', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'account_type')
    readonly_fields = ('date_joined', 'last_login')  # Mark non-editable fields as read-only
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'account_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone_number', 'account_type', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(Account, AccountAdmin)


@admin.register(AccountBalance)
class AccountBalanceAdmin(admin.ModelAdmin):
    list_display = ('account', 'available_balance', 'loan_balance', 'total_credits', 'total_debits','gbp','eur')
    search_fields = ('account__email',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor', 'card_type', 'account', 'status')
    search_fields = ('user__email', 'account')


class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'loan_type', 'status', 'date', 'approval_date', 'disbursement_date')
    list_filter = ('status', 'loan_type', 'currency')
    search_fields = ('user__email', 'loan_type', 'status', 'reason')
    ordering = ('-date',)
    readonly_fields = ('date', 'approval_date', 'disbursement_date', 'interest_rate')

    actions = ['approve_loans', 'decline_loans']  # Add custom actions

    def approve_loans(self, request, queryset):
        for loan_request in queryset:
            loan_request.status = 'approved'
            loan_request.approval_date = timezone.now()
            loan_request.disbursement_date = timezone.now()  # Set disbursement date to now
            
            # Update the user's account balance
            account_balance = AccountBalance.objects.get(account=loan_request.user)
            account_balance.loan_balance += loan_request.amount  # Update loan balance
            account_balance.available_balance += loan_request.amount  # Deduct from available balance
            
            # Save the updated account balance
            account_balance.save()
            loan_request.save()  # Save the loan request
            
            messages.success(request, f'Loan request for {loan_request.user.email} approved.')
    
    approve_loans.short_description = "Approve selected loan requests"

    def decline_loans(self, request, queryset):
        for loan_request in queryset:
            loan_request.status = 'declined'
            loan_request.approval_date = None  # Clear approval date if declined
            loan_request.disbursement_date = None  # Clear disbursement date if declined
            loan_request.save()  # Save the loan request
            
            messages.success(request, f'Loan request for {loan_request.user.email} declined.')

    decline_loans.short_description = "Decline selected loan requests"

# Register the LoanRequest model with the admin
admin.site.register(LoanRequest, LoanRequestAdmin)

@admin.register(Exchange)
class ExchangeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'from_currency', 'to_currency', 'status', 'date')
    search_fields = ('user',)
    list_filter = ('status', 'from_currency', 'to_currency', 'date')


@admin.register(ResetPassword)
class ResetPasswordAdmin(admin.ModelAdmin):
    list_display = ('email','reset_code','created_at')

@admin.register(TransferCode)
class TransferCodeAdmin(admin.ModelAdmin):
    list_display = ('transfer_code',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'user', 
        'transaction_date', 
        'amount', 
        'transaction_type', 
        'status', 
        'reference', 
        'institution', 
        'region', 
        'from_account', 
        'to_account'
    )
    search_fields = (
        'user__email', 
        'reference', 
        'institution', 
        'region', 
        'from_account', 
        'to_account'
    )
    list_filter = (
        'transaction_type', 
        'status', 
        'institution', 
        'region'
    )


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'TNX', 'network', 'rate', 'date', 'status', 'confirm_button', 'cancel_button')
    search_fields = ('user__email', 'TNX', 'network')
    list_filter = ('status', 'network', 'date')
    actions = ['confirm_deposit', 'cancel_deposit']

    def confirm_button(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a href="?confirm_deposit={}" style="padding: 6px 12px; background-color: #28a745; color: white; border-radius: 5px; text-decoration: none; font-weight: bold;">Confirm</a>',
                obj.id
            )
        return format_html(
            '<span style="padding: 6px 12px; background-color: #6c757d; color: white; border-radius: 5px; font-weight: bold;">Confirmed</span>'
        )
    confirm_button.short_description = 'Confirm'

    def cancel_button(self, obj):
        if obj.status == 'pending':
            return format_html(
                '<a href="?cancel_deposit={}" style="padding: 6px 12px; background-color: #dc3545; color: white; border-radius: 5px; text-decoration: none; font-weight: bold;"> Cancel</a>',
                obj.id
            )
        return format_html(
            '<span style="padding: 6px 12px; background-color: #6c757d; color: white; border-radius: 5px; font-weight: bold;"> Canceled</span>'
        )
    cancel_button.short_description = 'Cancel'

    def get_queryset(self, request):
        """Handles confirmation or cancellation via URL parameters."""
        qs = super().get_queryset(request)

        confirm_id = request.GET.get('confirm_deposit')
        cancel_id = request.GET.get('cancel_deposit')

        if confirm_id:
            deposit = get_object_or_404(Deposit, id=confirm_id)
            if deposit.status == 'pending':
                self.confirm_single_deposit(deposit)
                messages.success(request, f"Deposit {deposit.id} has been confirmed.")

        if cancel_id:
            deposit = get_object_or_404(Deposit, id=cancel_id)
            if deposit.status == 'pending':
                self.cancel_single_deposit(deposit)
                messages.warning(request, f"Deposit {deposit.id} has been canceled.")

        return qs

    def confirm_single_deposit(self, deposit):
        """Confirm a single deposit and update balance"""
        user_balance = AccountBalance.objects.get(account=deposit.user)
        user_balance.available_balance += deposit.amount
        user_balance.total_credits += deposit.amount
        user_balance.save()

        deposit.status = 'completed'
        deposit.save()

        transaction = Transaction.objects.filter(
            user=deposit.user, amount=deposit.amount, transaction_type='deposit'
        ).first()
        if transaction:
            transaction.status = 'completed'
            transaction.save()

    def cancel_single_deposit(self, deposit):
        """Cancel a single deposit"""
        deposit.status = 'failed'
        deposit.save()

        transaction = Transaction.objects.filter(
            user=deposit.user, amount=deposit.amount, transaction_type='deposit'
        ).first()
        if transaction:
            transaction.status = 'failed'
            transaction.save()

    def confirm_deposit(self, request, queryset):
        """Bulk confirm deposits"""
        for deposit in queryset:
            if deposit.status == 'pending':
                self.confirm_single_deposit(deposit)
        messages.success(request, "Selected deposits have been confirmed.")

    confirm_deposit.short_description = "Confirm selected deposits"

    def cancel_deposit(self, request, queryset):
        """Bulk cancel deposits"""
        for deposit in queryset:
            if deposit.status == 'pending':
                self.cancel_single_deposit(deposit)
        messages.warning(request, "Selected deposits have been canceled.")

    cancel_deposit.short_description = "Cancel selected deposits"




@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = (
        "reference", "user", "amount", "currency", "bank_name",
        "bank_account", "status", "date", "confirm_button", "cancel_button"
    )
    list_filter = ("status", "currency", "region", "bank_name", "date")
    search_fields = ("reference", "user__username", "bank_name", "bank_account", "sender_name")
    ordering = ("-date",)
    readonly_fields = ("reference", "user", "date", "charge")

    fieldsets = (
        ("Transfer Details", {
            "fields": ("reference", "user", "amount", "currency", "charge", "reason", "region", "status")
        }),
        ("Bank Details", {
            "fields": ("bank_country", "bank_name", "bank_account", "bank_holder", "identifier", "identifier_code", "sender_name")
        }),
    )

    actions = ["approve_transfer", "reject_transfer"]

    def confirm_button(self, obj):
        if obj.status == "pending":
            return format_html(
                '<a href="?confirm_transfer={}" style="padding:6px 12px; background-color:#28a745; color:white; border-radius:5px; text-decoration:none; font-weight:bold;">Confirm</a>',
                obj.id
            )
        return format_html(
            '<span style="padding:6px 12px; background-color:#6c757d; color:white; border-radius:5px; font-weight:bold;">Confirmed</span>'
        )
    confirm_button.short_description = "Confirm"

    def cancel_button(self, obj):
        if obj.status == "pending":
            return format_html(
                '<a href="?cancel_transfer={}" style="padding:6px 12px; background-color:#dc3545; color:white; border-radius:5px; text-decoration:none; font-weight:bold;">Cancel</a>',
                obj.id
            )
        return format_html(
            '<span style="padding:6px 12px; background-color:#6c757d; color:white; border-radius:5px; font-weight:bold;">Canceled</span>'
        )
    cancel_button.short_description = "Cancel"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # Check for query parameters for individual transfer actions.
        confirm_id = request.GET.get("confirm_transfer")
        cancel_id = request.GET.get("cancel_transfer")

        if confirm_id:
            transfer = get_object_or_404(Transfer, id=confirm_id)
            if transfer.status == "pending":
                self.confirm_single_transfer(transfer)
                messages.success(request, f"Transfer {transfer.reference} has been confirmed.")
        if cancel_id:
            transfer = get_object_or_404(Transfer, id=cancel_id)
            if transfer.status == "pending":
                self.cancel_single_transfer(transfer)
                messages.warning(request, f"Transfer {transfer.reference} has been canceled.")

        return qs

    def confirm_single_transfer(self, transfer):
        """Confirm a single transfer and update corresponding transaction."""
        transfer.status = "completed"
        transfer.save()
        transaction = Transaction.objects.filter(
            user=transfer.user,
            amount=transfer.amount,
            transaction_type="transfer",
            reference=transfer.reference
        ).first()
        if transaction:
            transaction.status = "completed"
            transaction.save()

    def cancel_single_transfer(self, transfer):
        """Cancel a single transfer and update corresponding transaction."""
        transfer.status = "failed"
        transfer.save()
        transaction = Transaction.objects.filter(
            user=transfer.user,
            amount=transfer.amount,
            transaction_type="transfer",
            reference=transfer.reference
        ).first()
        if transaction:
            transaction.status = "failed"
            transaction.save()

    def approve_transfer(self, request, queryset):
        """Bulk approve transfers."""
        for transfer in queryset:
            if transfer.status == "pending":
                self.confirm_single_transfer(transfer)
        messages.success(request, "Selected transfers have been approved.")

    approve_transfer.short_description = "Approve selected transfers"

    def reject_transfer(self, request, queryset):
        """Bulk reject transfers."""
        for transfer in queryset:
            if transfer.status == "pending":
                self.cancel_single_transfer(transfer)
        messages.warning(request, "Selected transfers have been rejected.")

    reject_transfer.short_description = "Reject selected transfers"






@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('network', 'deposit_address', 'instructions')
    search_fields = ('network', 'deposit_address')
    list_filter = ('network',)






@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('eur_usd', 'gbp_usd', 'eur_gbp', 'updated_at')
    search_fields = ('eur_usd', 'gbp_usd', 'eur_gbp')
    list_filter = ('updated_at',)

