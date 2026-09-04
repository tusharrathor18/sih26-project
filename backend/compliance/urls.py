from django.urls import path
from .views import ComplianceStatusView

urlpatterns = [
    path('status/', ComplianceStatusView.as_view(), name='compliance-status'),
]
