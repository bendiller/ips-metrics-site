from django.urls import path
from . import views

urlpatterns = [
    path('', views.not_found, name='not_found'),
    path('sandbox', views.sandbox, name='sandbox'),
    path('upcoming', views.upcoming, name='upcoming'),
]
