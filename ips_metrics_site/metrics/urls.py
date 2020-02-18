from django.urls import path
from . import views

urlpatterns = [
    path('', views.Upcoming.as_view(), name='upcoming'),
    path('upcoming/<int:days>', views.Upcoming.as_view(), name='upcoming'),
    path('ipf/<int:ipf_num>', views.IPFDetail.as_view(), name='ipf-detail'),
    path('repopulate/<int:ipf_num>', views.Repopulate.as_view(), name='repopulate'),
]
