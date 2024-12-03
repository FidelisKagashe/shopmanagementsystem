from django.urls import path
from . import views
from .views import *
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('lockout/', lockout_view, name='lockout'),
    path('logout/', views.logout_view, name='logout'),
    path('about/', views.About, name='about'),
    path('shop/', views.Shop, name='shop'),
    path('faq/', views.Faq, name='faq'),
    # path('landing/', views.Landing, name='landing'),
    path('contact/', views.Contact, name='contact'),
]
