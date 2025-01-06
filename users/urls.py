from django.urls import path
from . import views
from .views import *
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('lockout/', lockout_view, name='lockout'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.About, name='about'),
    path('shop/', views.Shop, name='shop'),
    path('faq/', views.Faq, name='faq'),
    path('myAccount/', views.MyAccount, name='myAccount'),
    # path('landing/', views.Landing, name='landing'),
    path('contact/', views.Contact, name='contact'),

    path('register/', views.register_email, name='register_email'),
    path('register/complete/', views.register_complete, name='register_complete'),

    # Password Reset Request: Simple FBV
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('reset/<uidb64>/<token>/<request_token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/<uidb64>/<token>/', views.password_reset_form, name='password_reset_form'),
    
    # Resend Reset Code (optional)
    path('resend_reset_code/', views.resend_reset_code, name='resend_reset_code'),  # Endpoint to resend the reset code
    
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='users/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'), name='password_change_done'),

]



