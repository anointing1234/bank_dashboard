"""
Django settings for bank_dash project.

Generated by 'django-admin startproject' using Django 5.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path
import os
import environ


from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR,'file.env'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b*fwsqx(&uk0a73ng+_@v2aza0&fe68v8i8kj4%#zw*1y7x@l4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


# ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://may2cu.com"]
ALLOWED_HOSTS = ["may2cu.com"]



# Application definition
AUTH_USER_MODEL = 'accounts.Account'

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    "django_extensions",
    'import_export',
    'accounts',
    'dash',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bank_dash.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bank_dash.wsgi.application'
 
 

AUTHENTICATION_BACKENDS = [
    'accounts.backends.AccountBackend',  # Custom backend for user login
    'django.contrib.auth.backends.ModelBackend',  # Default backend for admin login
] 

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),  
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

  
# DATABASES = {
#     'default': {
#         'ENGINE':'django.db.backends.postgresql',
#         'NAME':'bank_dash',
#         'USER':'postgres',
#         'PASSWORD':'1234',
#         'HOST':'localhost',  
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = '/media/'



# if DEBUG:
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# else:
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False




UNFOLD = {
    "SITE_HEADER": "mybcplc",
    "SHOW_SIDEBAR": True,
    "SITE_TITLE": "mybcplc",
    "SITE_SUBHEADER": "mybcplc",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: static("assets/img/bank_logo.png"),
        "dark": lambda request: static("assets/img/bank_logo.png"),
    },
    "SITE_LOGO": {
        "light": lambda request: static("assets/img/bank_logo.png"),
        "dark": lambda request: static("assets/img/bank_logo.png"),
    },
    "DASHBOARD": {
        "show_search": True,
        "show_all_applications": True,
        "cards": [
            {
                "title": _("Users"),
                "icon": "group",
                "link": reverse_lazy("admin:accounts_account_changelist"),
                "description": _("Manage users in the system."),
            },
            {
                "title": _("Deposits"),
                "icon": "account_balance",
                "link": reverse_lazy("admin:accounts_deposit_changelist"),
                "description": _("Manage deposits."),
            },
            {
                "title": _("Transfers"),
                "icon": "swap_horiz",
                "link": reverse_lazy("admin:accounts_transfer_changelist"),
                "description": _("Manage transfers."),
            },
            {
                "title": _("Transactions"),
                "icon": "receipt",
                "link": reverse_lazy("admin:accounts_transaction_changelist"),
                "description": _("Manage transactions."),
            },
        ],
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Menu"),
                "icon": "account_circle",
                "collapsible": False,
                "items": [
                    {
                        "title": _("Users"),
                        "icon": "group",
                        "link": reverse_lazy("admin:accounts_account_changelist"),
                    },
                    {
                        "title": _("Account Balances"),
                        "icon": "account_balance_wallet",
                        "link": reverse_lazy("admin:accounts_accountbalance_changelist"),
                    },
                ],
            },
            {
                "title": _("Banking & Cards"),
                "icon": "credit_card",
                "collapsible": False,
                "separator": True,
                "items": [
                    {
                        "title": _("Cards"),
                        "icon": "credit_card",
                        "link": reverse_lazy("admin:accounts_card_changelist"),
                    },
                    {
                        "title": _("Deposits"),
                        "icon": "account_balance",
                        "link": reverse_lazy("admin:accounts_deposit_changelist"),
                    },
                    {
                        "title": _("Transfers"),
                        "icon": "swap_horiz",
                        "link": reverse_lazy("admin:accounts_transfer_changelist"),
                    },
                      {
                        "title": _("Transfer codes"),
                        "icon": "swap_horiz",
                        "link": reverse_lazy("admin:accounts_transfercode_changelist"),
                    },
                  
                ],
            },
            {
                "title": _("Finances"),
                "icon": "attach_money",
                "collapsible": True,
                "separator": True,
                "items": [
                    {
                        "title": _("Exchanges"),
                        "icon": "currency_exchange",
                        "link": reverse_lazy("admin:accounts_exchange_changelist"),
                    },
                    {
                        "title": _("Exchange Rates"),
                        "icon": "bar_chart",
                        "link": reverse_lazy("admin:accounts_exchangerate_changelist"),
                    },
                    {
                        "title": _("Loan Requests"),
                        "icon": "request_quote",
                        "link": reverse_lazy("admin:accounts_loanrequest_changelist"),
                    },
                    {
                        "title": _("Payment Gateways"),
                        "icon": "payment",
                        "link": reverse_lazy("admin:accounts_paymentgateway_changelist"),
                    },
                    {
                        "title": _("Transactions"),
                        "icon": "receipt",
                        "link": reverse_lazy("admin:accounts_transaction_changelist"),
                    },
                ],
            },
        ],
    },
}