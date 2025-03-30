from django.urls import path
from django.contrib.auth import views as auth_views  # Adaugă această linie
from . import dash_app
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="index.html"), name='dash_app_index'),
    path('home/', TemplateView.as_view(template_name="home.html"), name='home'),
    path('download/', TemplateView.as_view(template_name="download.html"), name='download'),
    path('stat/', TemplateView.as_view(template_name="stat.html"), name='stat'),
    path('comp/', TemplateView.as_view(template_name="comp.html"), name='comp'),
    path('login/', TemplateView.as_view(template_name="login.html"), name='login'),
    path('register/', TemplateView.as_view(template_name="register.html"), name='register'),
    path('contact/', TemplateView.as_view(template_name="contact.html"), name='contact'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]

