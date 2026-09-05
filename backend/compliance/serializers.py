from rest_framework import serializers

from .models import CommodityCategory, ComplianceEvaluation, ComplianceResult, Rule, StandardPackSize


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"
        read_only_fields = ["created_at", "updated_at"]


class ComplianceResultSerializer(serializers.ModelSerializer):
    rule_reference = serializers.SerializerMethodField()
    source_image_id = serializers.IntegerField(source="source_image_id", read_only=True)

    class Meta:
        model = ComplianceResult
        fields = ["id", "rule_reference", "status", "detected_value", "expected_requirement", "evidence", "source_image_id", "source_ocr_field", "severity", "explanation", "recommendation", "evaluated_at"]

    def get_rule_reference(self, obj):
        return {"rule_number": obj.rule.rule_number, "sub_rule": obj.rule.sub_rule, "title": obj.rule.title, "source_page": obj.rule.source_page, "source_reference": obj.rule.source_reference}


class ComplianceEvaluationSerializer(serializers.ModelSerializer):
    results = ComplianceResultSerializer(many=True, read_only=True)

    class Meta:
        model = ComplianceEvaluation
        fields = ["id", "inspection", "overall_status", "total_rules", "passed", "failed", "warnings", "manual_review", "not_applicable", "evaluated_at", "results"]


class CommodityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CommodityCategory
        fields = "__all__"


class StandardPackSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StandardPackSize
        fields = "__all__"
