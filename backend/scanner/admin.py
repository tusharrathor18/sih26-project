from django.contrib import admin

from .models import AuditLog, ExtractedProductData, FieldCorrection, Inspection, InspectionImage, OCRResult


class InspectionImageInline(admin.TabularInline):
    model = InspectionImage
    extra = 0
    readonly_fields = ("uploaded_at", "file_size", "width", "height", "quality_score", "processing_status")


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ("inspection_id", "officer", "product_name", "status", "created_at", "verified_at")
    list_filter = ("status", "created_at")
    search_fields = ("inspection_id", "product_name", "officer__username")
    readonly_fields = ("inspection_id", "created_at", "updated_at", "verified_at")
    inlines = (InspectionImageInline,)


@admin.register(InspectionImage)
class InspectionImageAdmin(admin.ModelAdmin):
    list_display = ("inspection", "original_filename", "image_type", "processing_status", "uploaded_at")
    list_filter = ("image_type", "processing_status")
    readonly_fields = ("uploaded_at", "file_size", "width", "height", "quality_score")


@admin.register(ExtractedProductData)
class ExtractedProductDataAdmin(admin.ModelAdmin):
    list_display = ("inspection", "verification_status", "verified_by", "verified_at", "updated_at")
    readonly_fields = ("original_values", "verified_by", "verified_at", "updated_at")


@admin.register(FieldCorrection)
class FieldCorrectionAdmin(admin.ModelAdmin):
    list_display = ("inspection", "field_name", "corrected_by", "created_at")
    readonly_fields = ("inspection", "field_name", "original_value", "corrected_value", "correction_reason", "corrected_by", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "inspection", "action", "user")
    list_filter = ("action", "timestamp")
    search_fields = ("inspection__inspection_id", "description", "user__username")
    readonly_fields = ("inspection", "user", "action", "description", "metadata", "previous_value", "new_value", "ip_address", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ("image", "engine", "average_confidence", "processed_at")
    readonly_fields = ("image", "raw_text", "regions", "average_confidence", "engine", "engine_version", "processed_at", "error_message")
