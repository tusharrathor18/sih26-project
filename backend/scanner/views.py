from pathlib import Path

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.permissions import IsInspectorOfficer

from .models import ExtractedProductData, Inspection
from .serializers import (
    InspectionCreateSerializer,
    InspectionImageSerializer,
    InspectionSerializer,
    InspectionVerificationSerializer,
)
from .services.extraction_service import save_extraction
from .services.image_processing import process_image
from .services.ocr_service import run_ocr
from .audit import record_audit
from .models import FieldCorrection

class ScannerStatusView(APIView):
    permission_classes = [IsInspectorOfficer]

    def get(self, request):
        return Response(
            {
                "module": "scanner",
                "status": "ready",
                "message": "Inspection pipeline is available."
            },
            status=status.HTTP_200_OK
        )


class InspectionAccessMixin:
    permission_classes = [IsInspectorOfficer]

    def get_queryset(self):
        queryset = Inspection.objects.select_related("officer", "verified_by").prefetch_related("images", "extracted_data")
        profile = getattr(self.request.user, "officer_profile", None)
        if profile and profile.role == "ADMIN":
            return queryset
        return queryset.filter(officer=self.request.user)


class InspectionListCreateView(InspectionAccessMixin, generics.ListCreateAPIView):
    serializer_class = InspectionSerializer

    def get_serializer_class(self):
        return InspectionCreateSerializer if self.request.method == "POST" else InspectionSerializer

    def perform_create(self, serializer):
        serializer.save(officer=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = serializer.save(officer=request.user)
        record_audit(request, inspection, "INSPECTION_CREATED", "Inspection created.")
        output = InspectionSerializer(inspection, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class InspectionDetailView(InspectionAccessMixin, generics.RetrieveAPIView):
    serializer_class = InspectionSerializer
    lookup_field = "inspection_id"


class InspectionImageCreateView(InspectionAccessMixin, APIView):
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request, inspection_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        serializer = InspectionImageSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data["image"]
        image = serializer.save(
            inspection=inspection,
            original_filename=Path(upload.name).name[:255],
            file_size=upload.size,
            image_order=inspection.images.count(),
        )
        inspection.status = Inspection.Status.CREATED
        inspection.save(update_fields=["status", "updated_at"])
        record_audit(request, inspection, "IMAGE_UPLOADED", f"Image uploaded: {image.original_filename}.", {"image_id": image.id, "image_type": image.image_type})
        return Response(InspectionImageSerializer(image, context={"request": request}).data, status=status.HTTP_201_CREATED)


class InspectionImageDeleteView(InspectionAccessMixin, APIView):
    def delete(self, request, inspection_id, image_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        image = generics.get_object_or_404(inspection.images.all(), id=image_id)
        image.delete()
        record_audit(request, inspection, "IMAGE_DELETED", "Inspection image deleted.", {"image_id": image_id})
        return Response(status=status.HTTP_204_NO_CONTENT)


class InspectionProcessView(InspectionAccessMixin, APIView):
    def post(self, request, inspection_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        images = list(inspection.images.all())
        if not images:
            return Response({"message": "Add at least one image before processing."}, status=status.HTTP_400_BAD_REQUEST)

        inspection.status = Inspection.Status.PROCESSING
        inspection.processing_error = ""
        inspection.save(update_fields=["status", "processing_error", "updated_at"])
        all_text = []
        failures = []
        for image in images:
            prepared = process_image(image)
            if not prepared["ok"]:
                failures.append("Image preprocessing failed.")
                continue
            ocr_result = run_ocr(image)
            if ocr_result.error_message:
                failures.append(ocr_result.error_message)
            elif ocr_result.raw_text:
                all_text.append(ocr_result.raw_text)

        if failures and not all_text:
            inspection.status = Inspection.Status.FAILED
            inspection.processing_error = "OCR processing failed. Install PaddleOCR or retry with clearer images."
            inspection.save(update_fields=["status", "processing_error", "updated_at"])
            return Response({"message": inspection.processing_error, "inspection": InspectionSerializer(inspection, context={"request": request}).data}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        save_extraction(inspection, "\n".join(all_text))
        record_audit(request, inspection, "OCR_COMPLETED", "OCR and structured extraction completed.", {"image_count": len(images)})
        inspection.status = Inspection.Status.AWAITING_VERIFICATION
        inspection.processing_error = "One or more images could not be processed." if failures else ""
        inspection.save(update_fields=["status", "processing_error", "updated_at"])
        return Response(InspectionSerializer(inspection, context={"request": request}).data)


class InspectionVerificationView(InspectionAccessMixin, APIView):
    @transaction.atomic
    def patch(self, request, inspection_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        data = generics.get_object_or_404(ExtractedProductData, inspection=inspection)
        serializer = InspectionVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data["values"]
        for field_name, corrected_value in values.items():
            original_value = data.values.get(field_name, "")
            if str(original_value) != str(corrected_value):
                FieldCorrection.objects.create(inspection=inspection, field_name=field_name, original_value=str(original_value), corrected_value=str(corrected_value), corrected_by=request.user)
                record_audit(request, inspection, "FIELD_CORRECTED", f"Field corrected: {field_name}.", {"field_name": field_name}, str(original_value), str(corrected_value))
        from compliance.models import ComplianceEvaluation
        current_evaluation = ComplianceEvaluation.objects.filter(inspection=inspection, is_current=True).first()
        if current_evaluation:
            current_evaluation.is_current = False
            current_evaluation.superseded_at = timezone.now()
            current_evaluation.save(update_fields=["is_current", "superseded_at"])
            record_audit(request, inspection, "COMPLIANCE_INVALIDATED", "Compliance results invalidated after extracted data changed.")
        data.values = values
        data.verification_status = ExtractedProductData.VerificationStatus.VERIFIED if values == data.original_values else ExtractedProductData.VerificationStatus.CORRECTED
        data.verified_by = request.user
        data.verified_at = timezone.now()
        data.save(update_fields=["values", "verification_status", "verified_by", "verified_at", "updated_at"])
        inspection.status = Inspection.Status.READY_FOR_COMPLIANCE
        inspection.verified_by = request.user
        inspection.verified_at = timezone.now()
        inspection.save(update_fields=["status", "verified_by", "verified_at", "updated_at"])
        record_audit(request, inspection, "INSPECTION_VERIFIED", "Extracted information verified by officer.")
        return Response(InspectionSerializer(inspection, context={"request": request}).data)


class InspectionReviewView(InspectionAccessMixin, generics.RetrieveAPIView):
    serializer_class = InspectionSerializer
    lookup_field = "inspection_id"


class InspectionHistoryView(InspectionAccessMixin, generics.ListAPIView):
    serializer_class = InspectionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()
        status_filter = self.request.query_params.get("status", "").strip()
        product = self.request.query_params.get("product", "").strip()
        if search:
            queryset = queryset.filter(inspection_id__icontains=search)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if product:
            queryset = queryset.filter(product_name__icontains=product)
        return queryset


class InspectionAuditView(InspectionAccessMixin, APIView):
    def get(self, request, inspection_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        return Response([{"action": item.action, "description": item.description, "metadata": item.metadata, "timestamp": item.timestamp} for item in inspection.audit_logs.all()])


class DashboardStatsView(InspectionAccessMixin, APIView):
    def get(self, request):
        from compliance.models import ComplianceEvaluation

        inspections = self.get_queryset()
        evaluations = ComplianceEvaluation.objects.filter(inspection__in=inspections, is_current=True)
        statuses = [item.overall_status for item in evaluations]
        return Response({
            "total_inspections": inspections.count(),
            "compliant": statuses.count("COMPLIANT"),
            "non_compliant": statuses.count("NON_COMPLIANT"),
            "needs_manual_review": statuses.count("NEEDS_MANUAL_REVIEW"),
            "inconclusive": statuses.count("INCONCLUSIVE"),
        })
