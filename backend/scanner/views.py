from pathlib import Path

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
        return Response(InspectionImageSerializer(image, context={"request": request}).data, status=status.HTTP_201_CREATED)


class InspectionImageDeleteView(InspectionAccessMixin, APIView):
    def delete(self, request, inspection_id, image_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        image = generics.get_object_or_404(inspection.images.all(), id=image_id)
        image.delete()
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
        inspection.status = Inspection.Status.AWAITING_VERIFICATION
        inspection.processing_error = "One or more images could not be processed." if failures else ""
        inspection.save(update_fields=["status", "processing_error", "updated_at"])
        return Response(InspectionSerializer(inspection, context={"request": request}).data)


class InspectionVerificationView(InspectionAccessMixin, APIView):
    def patch(self, request, inspection_id):
        inspection = generics.get_object_or_404(self.get_queryset(), inspection_id=inspection_id)
        data = generics.get_object_or_404(ExtractedProductData, inspection=inspection)
        serializer = InspectionVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = serializer.validated_data["values"]
        data.values = values
        data.verification_status = ExtractedProductData.VerificationStatus.VERIFIED if values == data.original_values else ExtractedProductData.VerificationStatus.CORRECTED
        data.verified_by = request.user
        data.verified_at = timezone.now()
        data.save(update_fields=["values", "verification_status", "verified_by", "verified_at", "updated_at"])
        inspection.status = Inspection.Status.READY_FOR_COMPLIANCE
        inspection.verified_by = request.user
        inspection.verified_at = timezone.now()
        inspection.save(update_fields=["status", "verified_by", "verified_at", "updated_at"])
        return Response(InspectionSerializer(inspection, context={"request": request}).data)
