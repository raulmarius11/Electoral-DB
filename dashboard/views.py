from django.http import HttpResponse
from .dash_app import app as dash_app  # Import the dash app instance
from django.shortcuts import render

def dash_view(request):
    return HttpResponse(dash_app.index())

def home_view(request):
    return render(request, 'home.html')

def download_view(request):
    return render(request, 'download.html')

def index_view(request):
    return render(request, 'index.html')


def stat_view(request):
    return render(request, 'stat.html')

def comp_view(request):
    return render(request, 'comp.html')

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

def contact_view(request):
    return render(request, 'contact.html')
