# authentication_usertype/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.register, name='signup'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('register/candidate/<int:user_id>/', views.candidate_register_extra, name='candidate_register_extra'),
    path('register/company/<int:user_id>/', views.company_register_extra, name='company_register_extra'),
    path('login/', views.LoginPage, name='login'),
    path('logout/', views.LogoutPage, name='logout'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'), 
]
