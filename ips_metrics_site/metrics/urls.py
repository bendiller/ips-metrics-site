from django.urls import path
from . import views

urlpatterns = [
    path('', views.not_found, name='not_found'),
    path('sandbox', views.sandbox, name='sandbox'),
    path('upcoming/<int:days>', views.Upcoming.as_view(), name='upcoming'),
    # path('ipf/<int:ipf_num>', views.IPFDetail.as_view(), name='ipf-detail'),
    path('ipf/<int:ipf_num>', views.IPFDetail.as_view(), name='ipf-detail'),
    path('ipf/<int:ipf_num>/<str:cmd>', views.IPFDetail.as_view(), name='ipf-detail'),
    path('ipf-detail-loader', views.IPFDetailLoader.as_view(), name='ipf-detail-loader'),

    path('upcoming-dev/<int:days>', views.UpcomingDev.as_view(), name='upcoming-dev'),
    path('ipf-dev/<int:ipf_num>', views.IPFDetailDev.as_view(), name='ipf-detail-dev'),
]
