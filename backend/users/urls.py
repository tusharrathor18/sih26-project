from django.urls import path
from .views import OfficerLoginView, OfficerProfileView, OfficerLogoutView

urlpatterns = [
    path('login/', OfficerLoginView.as_view(), name='officer-login'),
    path('me/', OfficerProfileView.as_view(), name='officer-me'),
    path('logout/', OfficerLogoutView.as_view(), name='officer-logout'),
]
