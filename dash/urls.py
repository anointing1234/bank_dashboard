from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.views.static import serve 
from django.conf.urls import handler404, handler500


urlpatterns = [
    path('',views.home_page,name='my-1'),
    path('dashboard/',views.home_view,name='dashboard'),
    path('contact_us/',views.contact_us,name='contact_us'),
    path('Branch_location/',views.Branch_location,name='Branch_location'),
    path('Mortgage_Team/',views.Mortgage_Team,name='Mortgage+Team'),
    path('Our_Legacy/',views.Our_Legacy,name='Our_Legacy'),
    path('Checking/',views.Checking,name='Checking'),
    path('Savings/',views.Savings,name='Savings'),
    path('Catastrophe_Savings/',views.Catastrophe_Savings,name='Catastrophe_Savings'),
    path('cd_ira/',views.cd_ira,name='cd_ira'),
    path('Business_Checking/',views.Business_Checking,name='Business_Checking'),
    path('Rates/',views.Rates,name='Rates'),
    path('Construction/',views.Construction,name='Construction'),
    path('Mortgage_Loans/',views.Mortgage_Loans,name='Mortgage_Loans'),
    path('Mortgage_Team/',views.Mortgage_Team,name='Mortgage_Team'),
    path('Calculators/',views.Calculators,name='Calculators'),
    path('Online_Services/',views.Online_Services,name='Online_Services'),
    path('Card_Services/',views.Card_Services,name='Card_Services'),
    path('Additional_Services/',views.Additional_Services,name='Additional_Services'),
    path('We_Care/',views.We_Care,name='We_Care'),
    path('Online_Education/',views.Online_Education,name='Online_Education'),
    path('Credit_Cards/',views.Credit_Cards,name='Credit_Cards'),
    path('Security/',views.Security,name='Security'),
    path('profile/',views.profile_view,name='profile'),
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# handler404 = views.custom_404_view
# handler500 = views.custom_500_view
 
 

