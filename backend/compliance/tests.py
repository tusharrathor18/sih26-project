from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from scanner.models import ExtractedProductData, Inspection

from .models import ComplianceEvaluation, Rule, ScheduleEntry
from .services.applicability import determine_applicability
from .services.rule_engine import save_evaluation


class ComplianceEngineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="compliance_user", password="TestPassword@123")
        self.inspection = Inspection.objects.create(
            officer=self.user,
            commodity_category="MINERAL_WATER",
            package_type="RETAIL",
            consumer_type="GENERAL",
            approximate_quantity=Decimal("500"),
            quantity_unit="ml",
        )
        for number, validation_type in [("3", "APPLICABILITY"), ("6", "DECLARATION_SET"), ("22", "MPE")]:
            Rule.objects.create(rule_number=number, title=f"Rule {number}", requirement="PDF requirement", validation_type=validation_type, source_page="5")
        ScheduleEntry.objects.create(schedule="FIRST", commodity="500–1000 g/ml", data={"max": 1000, "mpe": 15, "kind": "absolute"}, source_page=28, source_reference="First Schedule")

    def test_industrial_consumer_is_not_applicable(self):
        self.inspection.consumer_type = "INDUSTRIAL"
        self.inspection.save()
        result = determine_applicability(self.inspection)
        self.assertEqual(result["status"], "NOT_APPLICABLE")

    def test_missing_physical_measurement_requires_manual_review(self):
        ExtractedProductData.objects.create(inspection=self.inspection, values={"net_quantity": "500", "quantity_unit": "ml"})
        evaluation, _ = save_evaluation(self.inspection)
        self.assertEqual(evaluation.results.get(rule__rule_number="22").status, "MANUAL_REVIEW")

    def test_measured_quantity_uses_first_schedule_mpe(self):
        self.inspection.actual_measured_quantity = Decimal("480")
        self.inspection.measurement_unit = "ml"
        self.inspection.save()
        ExtractedProductData.objects.create(inspection=self.inspection, values={"net_quantity": "500", "quantity_unit": "ml"})
        evaluation, _ = save_evaluation(self.inspection)
        self.assertEqual(evaluation.results.get(rule__rule_number="22").status, "FAIL")

    def test_missing_declaration_is_manual_review_not_fail(self):
        ExtractedProductData.objects.create(inspection=self.inspection, values={"net_quantity": "500", "quantity_unit": "ml"})
        evaluation, _ = save_evaluation(self.inspection)
        self.assertEqual(evaluation.results.get(rule__rule_number="6").status, "MANUAL_REVIEW")

    def test_rerun_creates_new_current_evaluation_version(self):
        ExtractedProductData.objects.create(inspection=self.inspection, values={"net_quantity": "500", "quantity_unit": "ml"})
        first, _ = save_evaluation(self.inspection)
        second, _ = save_evaluation(self.inspection)
        self.assertEqual(first.evaluation_version, 1)
        self.assertEqual(second.evaluation_version, 2)
        self.assertFalse(first.is_current)
        self.assertTrue(second.is_current)
