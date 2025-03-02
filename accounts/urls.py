from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve 


urlpatterns = [ 
    path('login/',views.login_view,name='login'),
    path('signup/',views.signup_view,name='signup'),
    path('register_view/',views.register,name='register_view'),
    path('login_Account/',views.login_Account,name='login_Account'),
    path('logout_view/',views.logout_view,name='logout_view'),
    path('deposit/',views.deposit_view,name='deposit'),
    path('transfer/',views.transfer_view,name='transfer'),
    path('validate_pin/',views.validate_pin, name='validate_pin'),
    path('Accounts/transaction_receipt/<str:reference>/',views.transaction_receipt, name='transaction_receipt'),
    path('get_payment_gateway/',views.get_payment_gateway,name='get_payment_gateway'),
    path('create_deposit/',views.create_deposit,name='create_deposit'),
    path("send-transfer-code/",views.send_transfer_code, name="send_transfer_code"),
    path("create_transfer/",views.create_transfer, name="create_transfer"),
    path('loan_view/',views.Loan_view,name='loan_view'),
    path('request_loan/',views.request_loan,name='request_loan'),
    path('update_fullname/',views.update_fullname,name='update_fullname'),
    path('exchange/',views.exchange_view,name='exchange'),
    path("swap-currency/",views.swap_currency, name="swap_currency"),
    path("cards/",views.cards_view,name='cards'),
    path('cards/add/',views.add_card, name='add_card'),
    path('send_reset_code_view/',views.send_reset_code_view,name='send_reset_code_view'),
    path('reset_password_view/',views.reset_password_view,name='reset_password_view'),
    path('send_pass/',views.send_pass,name='send_pass'),
    path('get_statements/',views.get_statements, name='get_statements'),
    path('validate_code/',views.validate_code,name='validate_code'),
    path('add_beneficiary/',views.add_beneficiary, name='add_beneficiary'),
    path('emails/',views.emails,name='emails'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('statements/deposit/',views.deposit_statements, name='deposit_statements'),
    path('statements/transfer/',views.transfer_statements, name='transfer_statements'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



 

