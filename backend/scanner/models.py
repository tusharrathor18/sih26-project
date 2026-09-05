import uuid

from django.conf import settings
from django.db import models


def inspection_image_path(instance, filename):
	return f"inspections/{instance.inspection.inspection_id}/original/{uuid.uuid4()}-{filename}"


def processed_image_path(instance, filename):
	return f"inspections/{instance.inspection.inspection_id}/processed/{uuid.uuid4()}-{filename}"


class Inspection(models.Model):
	class Status(models.TextChoices):
		CREATED = "CREATED", "Created"
		PROCESSING = "PROCESSING", "Processing"
		OCR_COMPLETE = "OCR_COMPLETE", "OCR complete"
		EXTRACTION_COMPLETE = "EXTRACTION_COMPLETE", "Extraction complete"
		AWAITING_VERIFICATION = "AWAITING_VERIFICATION", "Awaiting verification"
		VERIFIED = "VERIFIED", "Verified"
		READY_FOR_COMPLIANCE = "READY_FOR_COMPLIANCE", "Ready for compliance"
		FAILED = "FAILED", "Failed"

	inspection_id = models.CharField(max_length=30, unique=True, editable=False)
	officer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="inspections")
	product_name = models.CharField(max_length=255, blank=True)
	commodity_category = models.CharField(max_length=80, blank=True)
	package_type = models.CharField(max_length=40, blank=True)
	consumer_type = models.CharField(max_length=40, blank=True)
	approximate_quantity = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
	quantity_unit = models.CharField(max_length=20, blank=True)
	actual_measured_quantity = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
	measurement_unit = models.CharField(max_length=20, blank=True)
	measurement_method = models.CharField(max_length=120, blank=True)
	sample_size = models.PositiveIntegerField(null=True, blank=True)
	lot_size = models.PositiveIntegerField(null=True, blank=True)
	observed_deficiency = models.DecimalField(max_digits=12, decimal_places=3, null=True, blank=True)
	status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
	processing_error = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	verified_at = models.DateTimeField(null=True, blank=True)
	verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_inspections")

	class Meta:
		ordering = ["-created_at"]

	def save(self, *args, **kwargs):
		if not self.inspection_id:
			self.inspection_id = f"INS-{uuid.uuid4().hex[:10].upper()}"
		super().save(*args, **kwargs)

	def __str__(self):
		return self.inspection_id


class InspectionImage(models.Model):
	class ImageType(models.TextChoices):
		FRONT = "FRONT", "Front"
		BACK = "BACK", "Back"
		SIDE = "SIDE", "Side"
		TOP = "TOP", "Top"
		BOTTOM = "BOTTOM", "Bottom"
		OTHER = "OTHER", "Other"

	inspection = models.ForeignKey(Inspection, on_delete=models.CASCADE, related_name="images")
	image = models.ImageField(upload_to=inspection_image_path)
	processed_image = models.ImageField(upload_to=processed_image_path, blank=True)
	original_filename = models.CharField(max_length=255)
	image_order = models.PositiveIntegerField(default=0)
	image_type = models.CharField(max_length=10, choices=ImageType.choices, default=ImageType.OTHER)
	file_size = models.PositiveIntegerField(default=0)
	width = models.PositiveIntegerField(null=True, blank=True)
	height = models.PositiveIntegerField(null=True, blank=True)
	quality_score = models.FloatField(null=True, blank=True)
	quality_warning = models.CharField(max_length=255, blank=True)
	processing_status = models.CharField(max_length=32, default="UPLOADED")
	uploaded_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["image_order", "uploaded_at"]


class OCRResult(models.Model):
	image = models.OneToOneField(InspectionImage, on_delete=models.CASCADE, related_name="ocr_result")
	raw_text = models.TextField(blank=True)
	regions = models.JSONField(default=list, blank=True)
	average_confidence = models.FloatField(null=True, blank=True)
	engine = models.CharField(max_length=100, blank=True)
	engine_version = models.CharField(max_length=50, blank=True)
	processed_at = models.DateTimeField(auto_now=True)
	error_message = models.TextField(blank=True)


class ExtractedProductData(models.Model):
	class VerificationStatus(models.TextChoices):
		DETECTED = "DETECTED", "Detected"
		NOT_DETECTED = "NOT_DETECTED", "Not detected"
		LOW_CONFIDENCE = "LOW_CONFIDENCE", "Low confidence"
		VERIFIED = "VERIFIED", "Verified"
		CORRECTED = "CORRECTED", "Corrected"

	inspection = models.OneToOneField(Inspection, on_delete=models.CASCADE, related_name="extracted_data")
	values = models.JSONField(default=dict, blank=True)
	original_values = models.JSONField(default=dict, blank=True)
	field_metadata = models.JSONField(default=dict, blank=True)
	verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.DETECTED)
	verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_product_data")
	verified_at = models.DateTimeField(null=True, blank=True)
	updated_at = models.DateTimeField(auto_now=True)
