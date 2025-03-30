from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),  # This remains for the dashboard app
    path('economic/', include('economic.urls')),  # This is for the newly renamed economic_app
    path('django_plotly_dash/', include('django_plotly_dash.urls', namespace='the_django_plotly_dash')),
    path('', include('dashboard.urls')),
]
