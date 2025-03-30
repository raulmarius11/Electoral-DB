from django.urls import path
from . import views  # Import the views from the current directory

urlpatterns = [
    path('rest/', views.rest_view, name='rest'),  # Use the custom view
]
