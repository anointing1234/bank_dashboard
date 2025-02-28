from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Account,ACCOUNT_TYPE_CHOICES,Transfer,LoanRequest,Card,Beneficiary
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
import re
from django.contrib.auth import get_user_model
import random





def generate_unique_account_number():
    """
    Generate a unique 10-digit account number.
    """
    while True:
        acct_num = "".join(str(random.randint(0, 9)) for _ in range(10))
        if not Account.objects.filter(account_number=acct_num).exists():
            return acct_num

class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your password',
                'type': 'password'
            }
        ),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Confirm your password',
                'type': 'password'
            }
        ),
        label="Confirm Password"
    )

    class Meta:
        model = Account
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'account_type',
            'password',
        ]
        widgets = {
            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter your email',
                    'type': 'email'
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'First Name',
                    'type': 'text'
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Last Name',
                    'type': 'text'
                }
            ),
            'phone_number': forms.TextInput(
                attrs={
                    'class': 'form-control form-control-lg',
                    'placeholder': 'Enter your phone number',
                    'type': 'number'
                }
            ),
            'account_type': forms.Select(
                attrs={
                    'class': 'form-select form-control-lg',
                },
                choices=Account.account_type  # Ensure this attribute exists on your Account model.
            ),
        }

    def clean(self):
        """Ensure both password fields match."""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        """Save the user with a hashed password and auto-generate a unique account number."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        # Auto-generate and assign a unique account number if not already set.
        if not user.account_number:
            user.account_number = generate_unique_account_number()
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    account_id = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your Account ID',
                'type': 'text'
            }
        ),
        label="Account ID"  # Set the label to "Account ID"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter your password',
                'type': 'password'
            }
        ),
        label=""
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override the label_tag method for each bound field to return an empty string
        for bound_field in self.visible_fields():
            bound_field.label_tag = lambda **kwargs: ""

    def clean(self):
        account_id = self.cleaned_data.get('account_id')
        password = self.cleaned_data.get('password')

        # Authenticate with either email or account_id
        user = authenticate(username=account_id, password=password)
        if user is None:
            raise forms.ValidationError("Invalid Account ID or password.")
        self.user_cache = user
        return self.cleaned_data

    def get_user(self):
        return self.user_cache



class TransferForm(forms.ModelForm):
    # Field to select an existing beneficiary (optional)
    beneficiary = forms.ModelChoiceField(
        queryset=Beneficiary.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control", "id": "id_beneficiary"})
    )
    # Fields for manually entering beneficiary details if none is selected
    new_full_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control manual-beneficiary-field",
            "placeholder": "Enter recipient's full name"
        })
    )
    new_account_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control manual-beneficiary-field",
            "placeholder": "Enter recipient's account number"
        })
    )
    new_bank_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control manual-beneficiary-field",
            "placeholder": "Enter recipient's bank name"
        })
    )
    new_identifier_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control manual-beneficiary-field",
            "placeholder": "Enter SWIFT/BIC (optional)"
        })
    )

    class Meta:
        model = Transfer
        fields = [
            "beneficiary", "amount", "currency", "reason", "region"
        ]
        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter amount",
                "step": "0.01",
                "required": True
            }),
            "currency": forms.Select(choices=[
                ("USD", "USD"),
                ("EUR", "EUR"),
                ("GBP", "GBP")
            ], attrs={"class": "form-control", "required": True}),
            "reason": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Purpose of transfer",
                "required": True
            }),
            "region": forms.Select(
                choices=[
                    ("wire", "Wire Transfer"),
                    ("local", "Local Transfer"),
                    ("internal", "Internal Transfer")
                ],
                attrs={"class": "form-control", "required": True}
            ),
        }

    def __init__(self, *args, **kwargs):
        # Expect the current user to be passed in so we can filter beneficiaries.
        user = kwargs.pop('user', None)
        self.user = user
        super(TransferForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['beneficiary'].queryset = Beneficiary.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        beneficiary = cleaned_data.get('beneficiary')
        if not beneficiary:
            new_full_name = cleaned_data.get('new_full_name')
            new_account_number = cleaned_data.get('new_account_number')
            new_bank_name = cleaned_data.get('new_bank_name')
            if not (new_full_name and new_account_number and new_bank_name):
                raise forms.ValidationError(
                    "Please select an existing beneficiary or fill in all beneficiary details manually."
                )
        return cleaned_data

    def save(self, commit=True):
        transfer = super().save(commit=False)
        if not self.cleaned_data.get('beneficiary'):
            new_full_name = self.cleaned_data.get('new_full_name')
            new_account_number = self.cleaned_data.get('new_account_number')
            new_bank_name = self.cleaned_data.get('new_bank_name')
            new_identifier_code = self.cleaned_data.get('new_identifier_code')
            
            # Check if a beneficiary with these details already exists for the user.
            existing_beneficiary = Beneficiary.objects.filter(
                user=self.user,
                full_name=new_full_name,
                account_number=new_account_number,
                bank_name=new_bank_name
            ).first()
            
            if existing_beneficiary:
                # Use the existing beneficiary.
                transfer.beneficiary = existing_beneficiary
                # Optionally, you might clear manual fields here if needed.
            else:
                # Create a new beneficiary since none exists.
                beneficiary = Beneficiary.objects.create(
                    user=self.user,
                    full_name=new_full_name,
                    account_number=new_account_number,
                    bank_name=new_bank_name,
                    swift_code=new_identifier_code
                )
                transfer.beneficiary = beneficiary
        if commit:
            transfer.save()
        return transfer





class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ["amount", "currency", "loan_type", "reason", "term_months", "collateral"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "id": "loan_amount", "step": "0.01"}),
            "currency": forms.Select(attrs={"class": "form-control"}),
            "loan_type": forms.TextInput(attrs={"class": "form-control"}),
            "reason": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "term_months": forms.NumberInput(attrs={"class": "form-control", "id": "term_months"}),
            "collateral": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get("amount")
        term_months = cleaned_data.get("term_months")

        # Simple Interest Rate Calculation Logic (Adjust as Needed)
        if amount and term_months:
            if amount > 1000:
                interest_rate = 10.0  # 5% for small loans
            elif amount > 5000:
                interest_rate = 15.5  # 7.5% for medium loans
            else:
                interest_rate = 20.0  # 10% for large loans

            # Adjust based on loan duration
            if term_months > 12:
                interest_rate += 2  # Increase rate for longer terms

            # Set the calculated interest rate in the model
            cleaned_data["interest_rate"] = interest_rate

        return cleaned_data        




class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['account', 'card_type', 'vendor', 'status', 'card_password']
        widgets = {
            'card_password': forms.PasswordInput(),
        }        











class SendresetcodeForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        help_text='Required. Enter your email address to receive a password reset code.'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Bootstrap classes and placeholders
        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()  # Get the custom user model
        if not User.objects.filter(email=email).exists():
            raise ValidationError('No user is associated with this email address.')
        return email
    



class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        help_text="Required. Enter your email address."
    )
    reset_code = forms.CharField(
        label="Reset Code",
        help_text="Required. Enter the reset code you received."
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(),
        min_length=8,
        help_text="Required. Minimum length is 8 characters."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(),
        help_text="Required. Please confirm your new password."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set Bootstrap classes and placeholders
        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        })
        self.fields['reset_code'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your reset code'
        })
        self.fields['new_password'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your new password'
        })
        self.fields['confirm_password'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm your new password'
        })

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise ValidationError("The two password fields must match.")

        return cleaned_data

