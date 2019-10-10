from django.urls import path
from . import views

urlpatterns = [
    path('sandbox', views.sandbox, name='sandbox')
]
