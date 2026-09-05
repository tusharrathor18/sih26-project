from django.urls import path
from .views import ComplianceDetailView, ComplianceEvaluateView, ComplianceStatusView, ComplianceSummaryView, RuleListView

urlpatterns = [
    path('status/', ComplianceStatusView.as_view(), name='compliance-status'),
    path('rules/', RuleListView.as_view(), name='rule-list'),
    path('inspections/<str:inspection_id>/evaluate/', ComplianceEvaluateView.as_view(), name='compliance-evaluate'),
    path('inspections/<str:inspection_id>/compliance/', ComplianceDetailView.as_view(), name='compliance-detail'),
    path('inspections/<str:inspection_id>/results/', ComplianceDetailView.as_view(), name='compliance-results'),
    path('inspections/<str:inspection_id>/compliance/summary/', ComplianceSummaryView.as_view(), name='compliance-summary'),
]
