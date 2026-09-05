from pathlib import Path

from PIL import Image
from rest_framework import serializers

from .models import AuditLog, ExtractedProductData, FieldCorrection, Inspection, InspectionImage, OCRResult


MAX_IMAGE_SIZE = 10 * 1024 * 1024


class OCRResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = OCRResult
        fields = ["raw_text", "regions", "average_confidence", "engine", "engine_version", "processed_at", "error_message"]


class InspectionImageSerializer(serializers.ModelSerializer):
    ocr_result = OCRResultSerializer(read_only=True)
    image_url = serializers.SerializerMethodField()
    processed_image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=True)

    class Meta:
        model = InspectionImage
        fields = [
            "id", "image", "image_url", "processed_image_url", "original_filename",
            "image_order", "image_type", "file_size", "width", "height", "quality_score",
            "quality_warning", "processing_status", "uploaded_at", "ocr_result",
        ]
        read_only_fields = ["id", "original_filename", "file_size", "width", "height", "quality_score", "quality_warning", "processing_status", "uploaded_at"]

    def validate_image(self, value):
        if value.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError("Image is too large. Maximum allowed size is 10 MB.")
        content_type = getattr(value, "content_type", "")
        if content_type and content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise serializers.ValidationError("Unsupported image format. Use JPEG, PNG, or WEBP.")
        if Path(value.name).suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            raise serializers.ValidationError("Unsupported image extension. Use JPG, PNG, or WEBP.")
        try:
            with Image.open(value) as image:
                image.verify()
        except (OSError, ValueError):
            raise serializers.ValidationError("The uploaded file is not a valid image.")
        value.seek(0)
        return value

    def get_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.image.url) if request and obj.image else None

    def get_processed_image_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.processed_image.url) if request and obj.processed_image else None


class ExtractedProductDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtractedProductData
        fields = ["values", "original_values", "field_metadata", "verification_status", "verified_at", "updated_at"]
        read_only_fields = ["original_values", "verified_at", "updated_at"]


class InspectionSerializer(serializers.ModelSerializer):
    images = InspectionImageSerializer(many=True, read_only=True)
    extracted_data = ExtractedProductDataSerializer(read_only=True)
    image_count = serializers.IntegerField(source="images.count", read_only=True)
    officer_name = serializers.CharField(source="officer.officer_profile.name", read_only=True)
    audit_logs = serializers.SerializerMethodField()
    corrections = serializers.SerializerMethodField()

    class Meta:
        model = Inspection
        fields = [
            "id", "inspection_id", "product_name", "status", "processing_error",
            "officer_name", "image_count", "images", "extracted_data", "created_at", "updated_at", "verified_at", "audit_logs", "corrections",
        ]
        read_only_fields = ["id", "inspection_id", "status", "processing_error", "officer_name", "image_count", "images", "extracted_data", "created_at", "updated_at", "verified_at", "audit_logs", "corrections"]

    def get_audit_logs(self, obj):
        return [{"action": item.action, "description": item.description, "timestamp": item.timestamp, "metadata": item.metadata} for item in obj.audit_logs.all()]

    def get_corrections(self, obj):
        return [{"field_name": item.field_name, "original_value": item.original_value, "corrected_value": item.corrected_value, "correction_reason": item.correction_reason, "corrected_by": item.corrected_by.officer_profile.name, "created_at": item.created_at} for item in obj.corrections.all()]


class InspectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inspection
        fields = [
            "product_name", "commodity_category", "package_type", "consumer_type",
            "approximate_quantity", "quantity_unit", "actual_measured_quantity",
            "measurement_unit", "measurement_method", "sample_size", "lot_size",
        ]


class InspectionVerificationSerializer(serializers.Serializer):
    values = serializers.DictField(child=serializers.CharField(allow_blank=True), allow_empty=True)
