from django.urls import path

from . import views

urlpatterns = [
    path('api/v1/', views.web_api_v1, name='web_api_v1'),
]
