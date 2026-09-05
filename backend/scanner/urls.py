from django.urls import path
from .views import (
    InspectionDetailView,
    InspectionImageCreateView,
    InspectionImageDeleteView,
    InspectionListCreateView,
    InspectionProcessView,
    InspectionReviewView,
    InspectionHistoryView,
    InspectionAuditView,
    DashboardStatsView,
    InspectionVerificationView,
    InspectionReportView,
    ScannerStatusView,
)

urlpatterns = [
    path('status/', ScannerStatusView.as_view(), name='scanner-status'),
    path('inspections/', InspectionListCreateView.as_view(), name='inspection-list-create'),
    path('inspections/history/', InspectionHistoryView.as_view(), name='inspection-history'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('inspections/<str:inspection_id>/', InspectionDetailView.as_view(), name='inspection-detail'),
    path('inspections/<str:inspection_id>/review/', InspectionReviewView.as_view(), name='inspection-review'),
    path('inspections/<str:inspection_id>/audit/', InspectionAuditView.as_view(), name='inspection-audit'),
    path('inspections/<str:inspection_id>/report/pdf/', InspectionReportView.as_view(), name='inspection-report-pdf'),
    path('inspections/<str:inspection_id>/images/', InspectionImageCreateView.as_view(), name='inspection-image-create'),
    path('inspections/<str:inspection_id>/images/<int:image_id>/', InspectionImageDeleteView.as_view(), name='inspection-image-delete'),
    path('inspections/<str:inspection_id>/process/', InspectionProcessView.as_view(), name='inspection-process'),
    path('inspections/<str:inspection_id>/verify/', InspectionVerificationView.as_view(), name='inspection-verify'),
]
