from django.urls import path
from . import views

urlpatterns = [
    path('', views.not_found, name='not_found'),
    path('sandbox', views.sandbox, name='sandbox'),
    path('upcoming/<int:days>', views.Upcoming.as_view(), name='upcoming'),
    # path('ipf/<int:ipf_num>', views.IPFDetail.as_view(), name='ipf-detail'),
    path('ipf/<int:ipf_num>', views.IPFDetail.as_view(), name='ipf-detail'),
    path('ipf-detail-loader', views.IPFDetailLoader.as_view(), name='ipf-detail-loader'),
    path('repopulate/<int:ipf_num>', views.Repopulate.as_view(), name='repopulate'),
]
