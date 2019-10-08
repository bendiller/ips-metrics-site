from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sub_page', views.sub_page, name='sub_page')
]