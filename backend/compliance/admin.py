from django.contrib import admin

from .models import CommodityCategory, ComplianceEvaluation, ComplianceResult, Exemption, Rule, ScheduleEntry, StandardPackSize


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ("rule_number", "sub_rule", "title", "validation_type", "is_active")
    list_filter = ("validation_type", "is_active")
    search_fields = ("rule_number", "title", "requirement")
    readonly_fields = ("created_at", "updated_at")

    def has_module_permission(self, request):
        return bool(request.user.is_superuser or getattr(getattr(request.user, "officer_profile", None), "role", "") == "ADMIN")

    def has_add_permission(self, request):
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_module_permission(request)


@admin.register(CommodityCategory)
class CommodityCategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")


@admin.register(StandardPackSize)
class StandardPackSizeAdmin(admin.ModelAdmin):
    list_display = ("category", "quantity_value", "quantity_unit", "source_page")
    list_filter = ("category", "quantity_unit")


@admin.register(ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ("schedule", "commodity", "source_page")
    list_filter = ("schedule",)
    search_fields = ("commodity", "source_reference")


@admin.register(Exemption)
class ExemptionAdmin(admin.ModelAdmin):
    list_display = ("code", "description", "is_active")


@admin.register(ComplianceEvaluation)
class ComplianceEvaluationAdmin(admin.ModelAdmin):
    list_display = ("inspection", "overall_status", "failed", "manual_review", "evaluated_at")
    readonly_fields = ("evaluated_at",)


@admin.register(ComplianceResult)
class ComplianceResultAdmin(admin.ModelAdmin):
    list_display = ("evaluation", "rule", "status", "severity", "evaluated_at")
    list_filter = ("status", "severity")
    search_fields = ("explanation", "recommendation")
    readonly_fields = ("evaluated_at",)
