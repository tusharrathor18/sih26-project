from django.db import models


class CommodityCategory(models.Model):
	code = models.CharField(max_length=80, unique=True)
	name = models.CharField(max_length=160)
	source_page = models.PositiveIntegerField(null=True, blank=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return self.name


class Rule(models.Model):
	rule_number = models.CharField(max_length=20)
	sub_rule = models.CharField(max_length=40, blank=True)
	title = models.CharField(max_length=255)
	requirement = models.TextField()
	applicability_condition = models.TextField(blank=True)
	validation_type = models.CharField(max_length=80, default="MANUAL_REVIEW")
	validation_config = models.JSONField(default=dict, blank=True)
	severity = models.CharField(max_length=20, default="WARNING")
	source_document = models.CharField(max_length=255, default="The Legal Metrology (Packaged Commodities) Rules, 2011.pdf")
	source_page = models.CharField(max_length=40, blank=True)
	source_reference = models.CharField(max_length=255, blank=True)
	schedule_reference = models.CharField(max_length=80, blank=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["rule_number", "sub_rule"]
		constraints = [models.UniqueConstraint(fields=["rule_number", "sub_rule"], name="unique_rule_reference")]

	def __str__(self):
		return f"Rule {self.rule_number}{self.sub_rule}"


class StandardPackSize(models.Model):
	category = models.ForeignKey(CommodityCategory, on_delete=models.CASCADE, related_name="standard_pack_sizes")
	quantity_value = models.DecimalField(max_digits=12, decimal_places=3)
	quantity_unit = models.CharField(max_length=20)
	conditions = models.TextField(blank=True)
	rule_reference = models.CharField(max_length=40, default="Rule 5")
	schedule_reference = models.CharField(max_length=80, default="Second Schedule")
	source_page = models.PositiveIntegerField(default=29)


class ScheduleEntry(models.Model):
	class Schedule(models.TextChoices):
		FIRST = "FIRST", "First Schedule"
		THIRD = "THIRD", "Third Schedule"
		FOURTH = "FOURTH", "Fourth Schedule"

	schedule = models.CharField(max_length=10, choices=Schedule.choices)
	commodity = models.CharField(max_length=180)
	data = models.JSONField(default=dict)
	source_page = models.PositiveIntegerField()
	source_reference = models.CharField(max_length=255, blank=True)


class Exemption(models.Model):
	code = models.CharField(max_length=80, unique=True)
	description = models.TextField()
	conditions = models.JSONField(default=dict)
	source_page = models.PositiveIntegerField(default=24)
	is_active = models.BooleanField(default=True)


class ComplianceEvaluation(models.Model):
	class OverallStatus(models.TextChoices):
		COMPLIANT = "COMPLIANT", "Compliant"
		NON_COMPLIANT = "NON_COMPLIANT", "Non-compliant"
		NEEDS_MANUAL_REVIEW = "NEEDS_MANUAL_REVIEW", "Needs manual review"
		INCONCLUSIVE = "INCONCLUSIVE", "Inconclusive"

	inspection = models.ForeignKey("scanner.Inspection", on_delete=models.CASCADE, related_name="compliance_evaluations")
	evaluation_version = models.PositiveIntegerField(default=1)
	is_current = models.BooleanField(default=True)
	superseded_at = models.DateTimeField(null=True, blank=True)
	overall_status = models.CharField(max_length=30, choices=OverallStatus.choices, default=OverallStatus.INCONCLUSIVE)
	total_rules = models.PositiveIntegerField(default=0)
	passed = models.PositiveIntegerField(default=0)
	failed = models.PositiveIntegerField(default=0)
	warnings = models.PositiveIntegerField(default=0)
	manual_review = models.PositiveIntegerField(default=0)
	not_applicable = models.PositiveIntegerField(default=0)
	evaluated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-evaluation_version"]
		constraints = [models.UniqueConstraint(fields=["inspection", "evaluation_version"], name="unique_inspection_evaluation_version")]


class ComplianceResult(models.Model):
	class Status(models.TextChoices):
		PASS = "PASS", "Pass"
		FAIL = "FAIL", "Fail"
		WARNING = "WARNING", "Warning"
		MANUAL_REVIEW = "MANUAL_REVIEW", "Manual review"
		NOT_APPLICABLE = "NOT_APPLICABLE", "Not applicable"
		NOT_DETECTED = "NOT_DETECTED", "Not detected"

	evaluation = models.ForeignKey(ComplianceEvaluation, on_delete=models.CASCADE, related_name="results")
	rule = models.ForeignKey(Rule, on_delete=models.PROTECT, related_name="compliance_results")
	status = models.CharField(max_length=20, choices=Status.choices)
	detected_value = models.TextField(blank=True)
	expected_requirement = models.TextField(blank=True)
	evidence = models.JSONField(default=dict, blank=True)
	source_image = models.ForeignKey("scanner.InspectionImage", on_delete=models.SET_NULL, null=True, blank=True)
	source_ocr_field = models.CharField(max_length=100, blank=True)
	severity = models.CharField(max_length=20, default="WARNING")
	explanation = models.TextField(blank=True)
	recommendation = models.TextField(blank=True)
	evaluated_at = models.DateTimeField(auto_now=True)
