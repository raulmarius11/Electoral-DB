from django.http import HttpResponse
from .economic_app import app as economic_app  # Import the dash app instance
from django.shortcuts import render

def economic_view(request):
    return HttpResponse(economic_app.index())  

def rest_view(request):
    return render(request, 'rest.html')