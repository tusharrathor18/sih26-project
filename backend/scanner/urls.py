from django.urls import path
from .views import ScannerStatusView

urlpatterns = [
    path('status/', ScannerStatusView.as_view(), name='scanner-status'),
]
