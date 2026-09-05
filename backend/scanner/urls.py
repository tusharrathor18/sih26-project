from django.urls import path
from .views import (
    InspectionDetailView,
    InspectionImageCreateView,
    InspectionImageDeleteView,
    InspectionListCreateView,
    InspectionProcessView,
    InspectionVerificationView,
    ScannerStatusView,
)

urlpatterns = [
    path('status/', ScannerStatusView.as_view(), name='scanner-status'),
    path('inspections/', InspectionListCreateView.as_view(), name='inspection-list-create'),
    path('inspections/<str:inspection_id>/', InspectionDetailView.as_view(), name='inspection-detail'),
    path('inspections/<str:inspection_id>/images/', InspectionImageCreateView.as_view(), name='inspection-image-create'),
    path('inspections/<str:inspection_id>/images/<int:image_id>/', InspectionImageDeleteView.as_view(), name='inspection-image-delete'),
    path('inspections/<str:inspection_id>/process/', InspectionProcessView.as_view(), name='inspection-process'),
    path('inspections/<str:inspection_id>/verify/', InspectionVerificationView.as_view(), name='inspection-verify'),
]
